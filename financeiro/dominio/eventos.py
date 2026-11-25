"""Eventos de domínio: fatos que já aconteceram (por isso imutáveis).

Carregam apenas identificadores e valores simples, nunca objetos de domínio:
quem reage não pode alterar a Conta por engano e o evento poderia virar
uma mensagem de fila sem mudar nada.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class LancamentoRegistrado:
    conta_id: str
    lancamento_id: str
    tipo: str          # "debito" ou "credito"
    valor: float
    saldo_apos: float


@dataclass(frozen=True)
class SaldoAjustado:
    conta_id: str
    ajuste: str        # "rendimento", "juros" ou "correcao"
    valor_aplicado: float
    saldo_apos: float
