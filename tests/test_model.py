import math

import pytest
import torch

from nhom19_process_xai.model.transformer import ModelConfig, ProcessTransformer, MultiHeadAttention


def model(profile="BASE"):
    torch.manual_seed(1729)
    return ProcessTransformer(ModelConfig(5, 3, 8, profile=profile))


def test_shape_padding_and_empty_rows():
    net = model().eval()
    tokens = torch.tensor([[2, 3], [0, 0]])
    valid = tokens != 0
    result = net(tokens, valid)
    assert result.logits.shape == (2, 3)
    assert result.attention_raw.shape == (2, 4, 2, 2)
    assert torch.allclose(result.attention_raw[0].sum(-1), torch.ones(4, 2))
    assert torch.count_nonzero(result.attention_raw[1]) == 0
    assert torch.isfinite(result.probabilities).all()
    padded = net(torch.tensor([[2, 3, 0]]), torch.tensor([[True, True, False]]))
    torch.testing.assert_close(result.logits[:1], padded.logits, atol=1e-6, rtol=1e-5)
    assert torch.count_nonzero(padded.attention_raw[:, :, 2, :]) == 0
    assert torch.count_nonzero(padded.attention_raw[:, :, :, 2]) == 0


def test_post_softmax_intervention_retains_mass():
    net = model().eval()
    tokens = torch.tensor([[2, 3]])
    valid = torch.ones_like(tokens, dtype=torch.bool)
    mask = torch.tensor([[False, True]])
    base = net(tokens, valid)
    result = net(tokens, valid, intervention=mask)
    torch.testing.assert_close(base.attention_raw, result.attention_raw)
    torch.testing.assert_close(result.attention_effective[:, :, 0, 0], base.attention_raw[:, :, 0, 0])
    assert torch.count_nonzero(result.attention_effective[:, :, 1, :]) == 0
    assert torch.count_nonzero(result.attention_effective[:, :, :, 1]) == 0
    author = net(tokens, valid, intervention=mask, mode="E3-AUTHOR")
    torch.testing.assert_close(author.attention_effective[:, :, 0, 0], torch.ones(1, 4))


@pytest.mark.parametrize("profile", ["BASE", "E2-FC", "E2-AC", "E2-UNI"])
def test_gradients_and_freeze(profile):
    net = model(profile)
    frozen_before = {n: p.detach().clone() for n, p in net.attention.named_parameters()}
    head_before = net.classifier_output.weight.detach().clone()
    opt = torch.optim.Adam(net.parameters(), lr=.001, eps=1e-7)
    tokens = torch.tensor([[2, 3], [2, 4]])
    output = net(tokens, torch.ones_like(tokens, dtype=torch.bool))
    torch.nn.functional.cross_entropy(output.logits, torch.tensor([0, 2])).backward()
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in net.parameters())
    opt.step()
    assert not torch.equal(head_before, net.classifier_output.weight)
    if profile != "BASE":
        assert all(torch.equal(frozen_before[n], p) for n, p in net.attention.named_parameters())
    if profile == "E2-UNI":
        torch.testing.assert_close(output.attention_raw, torch.full((2, 4, 2, 2), .5))


def test_frozen_constants_counterexample():
    attention = model("E2-FC").attention
    hidden = torch.zeros(1, 2, 36)
    hidden[0, 0, 0] = 1
    hidden[0, 1, 0] = 2
    _, scores, _ = attention(hidden, torch.ones(1, 2, dtype=torch.bool))
    expected = torch.tensor([.0003, .0006]).softmax(0)
    torch.testing.assert_close(scores[0, 0, 0], expected)
    assert abs(float(scores[0, 0, 0, 1] - scores[0, 0, 0, 0])) > 1e-6


def test_attention_hand_computed():
    attention = MultiHeadAttention(ModelConfig(3, 2, 2, d_model=2, num_heads=1, d_head=1))
    with torch.no_grad():
        attention.query.weight.copy_(torch.tensor([[1., 0.]]))
        attention.key.weight.copy_(torch.tensor([[0., 1.]]))
        attention.value.weight.copy_(torch.tensor([[2., 4./math.log(3)]]))
        attention.query.bias.zero_()
        attention.key.bias.zero_()
        attention.value.bias.zero_()
        attention.output.weight.fill_(1)
        attention.output.bias.zero_()
    context, scores, _ = attention(torch.tensor([[[1., 0.], [1., math.log(3)]]]),
                                    torch.ones(1, 2, dtype=torch.bool))
    torch.testing.assert_close(scores, torch.tensor([[[[.25,.75],[.25,.75]]]]))
    torch.testing.assert_close(context, torch.full((1, 2, 2), 5.))


def test_state_roundtrip_and_eval_repeat(tmp_path):
    net = model().eval()
    ids = torch.tensor([[2, 3]])
    valid = ids != 0
    output = net(ids, valid)
    target = tmp_path / "weights.pt"
    torch.save(net.state_dict(), target)
    restored = model().eval()
    restored.load_state_dict(torch.load(target, weights_only=True))
    torch.testing.assert_close(output.logits, restored(ids, valid).logits, rtol=0, atol=0)
    torch.testing.assert_close(output.logits, net(ids, valid).logits, rtol=0, atol=0)


def test_four_nine_dimensional_heads_scale_and_concatenate():
    attention = MultiHeadAttention(ModelConfig(5, 3, 2))
    with torch.no_grad():
        for layer in (attention.query, attention.key, attention.value, attention.output):
            layer.weight.zero_()
            layer.bias.zero_()
        attention.output.weight.copy_(torch.eye(36))
        for head in range(4):
            coordinate = head * 9
            attention.query.weight[coordinate, 0] = 1
            attention.key.weight[coordinate, 1] = 1
            attention.value.weight[coordinate, 0] = 2 + head
            attention.value.weight[coordinate, 1] = 4 / (3 * math.log(3))
    hidden = torch.zeros(1, 2, 36)
    hidden[:, :, 0] = 1
    hidden[:, 1, 1] = 3 * math.log(3)
    context, raw, effective = attention(hidden, torch.ones(1, 2, dtype=torch.bool))

    # Each head has logits [0, 3 ln(3)] / sqrt(9), giving [.25, .75].
    expected_weights = torch.tensor([.25, .75]).expand(1, 4, 2, 2)
    torch.testing.assert_close(raw, expected_weights, atol=1e-6, rtol=0)
    torch.testing.assert_close(effective, raw, atol=0, rtol=0)
    expected_context = torch.zeros(1, 2, 36)
    expected_context[:, :, [0, 9, 18, 27]] = torch.tensor([5., 6., 7., 8.])
    torch.testing.assert_close(context, expected_context, atol=1e-6, rtol=0)
