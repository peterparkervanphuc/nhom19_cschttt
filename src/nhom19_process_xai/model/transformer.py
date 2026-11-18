"""One encoder block with four nine-dimensional heads (paper Figure 1).

No dependency on the reference repository. Masks distinguish structural padding
from a post-softmax experimental intervention so residuals retain their inputs.
"""

from dataclasses import dataclass
import math

import torch
from torch import Tensor, nn


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int
    num_classes: int
    max_positions: int
    d_model: int = 36
    num_heads: int = 4
    d_head: int = 9
    ff_dim: int = 64
    dropout: float = .1
    profile: str = "BASE"

    def __post_init__(self):
        if min(self.vocab_size, self.num_classes, self.max_positions,
               self.d_model, self.num_heads, self.d_head, self.ff_dim) < 1:
            raise ValueError("Model dimensions must be positive")
        if not 0 <= self.dropout < 1:
            raise ValueError("Dropout must be in [0,1)")
        if self.profile not in {"BASE", "E2-FC", "E2-AC", "E2-UNI"}:
            raise ValueError("Unknown model profile")


@dataclass
class ModelOutput:
    logits: Tensor
    probabilities: Tensor
    attention_raw: Tensor
    attention_effective: Tensor


class MultiHeadAttention(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.heads = config.num_heads
        self.width = config.d_head
        self.uniform = config.profile == "E2-UNI"
        projected = self.heads * self.width
        self.query = nn.Linear(config.d_model, projected)
        self.key = nn.Linear(config.d_model, projected)
        self.value = nn.Linear(config.d_model, projected)
        self.output = nn.Linear(projected, config.d_model)

    def forward(self, hidden: Tensor, valid: Tensor,
                intervention: Tensor | None = None,
                mode: str = "E3-PAPER") -> tuple[Tensor, Tensor, Tensor]:
        batch, length, _ = hidden.shape
        def project(layer: nn.Linear) -> Tensor:
            return layer(hidden).reshape(batch, length, self.heads, self.width).transpose(1, 2)

        queries, keys, values = project(self.query), project(self.key), project(self.value)
        logits = queries @ keys.transpose(-2, -1) / math.sqrt(self.width)
        if self.uniform:
            logits = torch.zeros_like(logits)
        score_valid = valid
        if intervention is not None and mode == "E3-AUTHOR":
            score_valid = valid & ~intervention
        key_mask = score_valid[:, None, None, :]
        masked_logits = logits.masked_fill(~key_mask, -torch.inf)
        # Avoid softmax(-inf,...,-inf) while preserving exact zero probabilities.
        has_keys = score_valid.any(-1)[:, None, None, None]
        masked_logits = torch.where(has_keys, masked_logits, torch.zeros_like(masked_logits))
        attention = masked_logits.softmax(-1) * key_mask
        attention = attention * score_valid[:, None, :, None]
        effective = attention
        if intervention is not None and mode == "E3-PAPER":
            retained = ~intervention
            effective = attention * retained[:, None, :, None] * retained[:, None, None, :]
        context = (effective @ values).transpose(1, 2).reshape(batch, length, self.heads * self.width)
        return self.output(context), attention, effective


class ProcessTransformer(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.activity = nn.Embedding(config.vocab_size, config.d_model)
        self.position = nn.Embedding(config.max_positions, config.d_model)
        self.attention = MultiHeadAttention(config)
        self.dropout = nn.Dropout(config.dropout)
        self.norm_attention = nn.LayerNorm(config.d_model, eps=1e-6)
        self.ffn = nn.Sequential(nn.Linear(config.d_model, config.ff_dim), nn.ReLU(),
                                 nn.Linear(config.ff_dim, config.d_model))
        self.norm_ffn = nn.LayerNorm(config.d_model, eps=1e-6)
        self.classifier_hidden = nn.Linear(config.d_model, config.ff_dim)
        self.classifier_output = nn.Linear(config.ff_dim, config.num_classes)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.uniform_(module.weight, -.05, .05)
        if self.config.profile != "BASE":
            for name, parameter in self.attention.named_parameters():
                if self.config.profile in {"E2-FC", "E2-UNI"}:
                    nn.init.constant_(parameter, 0 if name.endswith("bias") else .01)
                parameter.requires_grad_(False)

    def forward(self, tokens: Tensor, valid: Tensor,
                position_ids: Tensor | None = None,
                intervention: Tensor | None = None,
                mode: str = "E3-PAPER") -> ModelOutput:
        if tokens.ndim != 2 or tokens.shape != valid.shape or tokens.shape[1] == 0:
            raise ValueError("tokens and valid must be equal [B,T] shapes with T>=1")
        if tokens.dtype != torch.int64 or valid.dtype != torch.bool:
            raise ValueError("tokens must be int64 and valid must be bool")
        if mode not in {"E3-PAPER", "E3-AUTHOR"}:
            raise ValueError("Unknown attention intervention mode")
        if intervention is not None and (intervention.shape != valid.shape or intervention.dtype != torch.bool):
            raise ValueError("Intervention must be a bool [B,T] tensor")
        if position_ids is None:
            position_ids = torch.arange(tokens.shape[1], device=tokens.device).expand_as(tokens)
        if position_ids.shape != tokens.shape or position_ids.dtype != torch.int64:
            raise ValueError("position_ids must be int64 [B,T]")
        if torch.any(position_ids < 0) or torch.any(position_ids >= self.config.max_positions):
            raise ValueError("Position exceeds configured context limit")
        hidden = self.activity(tokens) + self.position(position_ids)
        attended, raw, effective = self.attention(hidden, valid, intervention, mode)
        hidden = self.norm_attention(hidden + self.dropout(attended))
        hidden = self.norm_ffn(hidden + self.dropout(self.ffn(hidden)))
        pooled = (hidden * valid.unsqueeze(-1)).sum(1) / valid.sum(1, keepdim=True).clamp_min(1)
        pooled = self.dropout(pooled)
        pooled = self.dropout(torch.relu(self.classifier_hidden(pooled)))
        logits = self.classifier_output(pooled)
        return ModelOutput(logits, logits.softmax(-1), raw, effective)
