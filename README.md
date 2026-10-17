# Camaleão Marketing Copilot

**Transforme arquivos de marketing em cálculos conferíveis e propostas para revisão no ChatGPT.**

Experimento PT-BR de Carlos Felipe: snapshot SEO, Search Console e mídia paga. Código original MIT, inspirado em padrões do [NotFair](https://github.com/nowork-studio/notfair-plugin/tree/c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d), com atribuição preservada. Não é fork completo, plataforma de anúncios ou serviço NotFair.

## Começar no ChatGPT

1. Abra [o guia de uso](chatgpt/COMECAR.md).
2. Copie [as instruções](chatgpt/INSTRUCOES.md) para um projeto no ChatGPT e disponibilize o exemplo/relatório desejado.
3. Peça: “Explique este relatório, separe fatos e hipóteses e proponha três testes. Não altere campanhas ou publique conteúdo.”

O guia está preparado; não foi instalado automaticamente na sua conta. Ferramentas de código e arquivos precisam estar acessíveis na sessão. Sem execução Python, a conversa pode fazer revisão qualitativa, mas deve declarar os cálculos não executados. Os 48 itens no [catálogo upstream](third_party/notfair/catalog.json) são referências, não skills instaladas.

## Três jornadas

| Jornada | O que entrega | Limite |
| --- | --- | --- |
| Snapshot SEO | Títulos, descrição, H1, canonical, robots meta e sintaxe JSON-LD | HTML fornecido; não visita site nem comprova indexação/posição/CWV |
| Search Console | CTR, posição ponderada e triagem de linhas | Export normalizado; completude e origem não verificadas |
| Mídia paga | Gasto, CTR, CPA e ROAS por canal, com período/atribuição | Valores declarados; sem deduplicar receitas ou recomendar gasto automático |

O motor **não faz requisições de rede, chamadas LLM/API, publicação ou alterações em contas**. Todo relatório permanece `review_status: pending`, `execution_allowed: false`. Hash e ponteiros vinculam a entrada; não autenticam export nem aprovação.

## Demonstração local reproduzível

Python 3.11+ em Linux/POSIX. Núcleo sem dependências runtime de terceiros. O CLI depende de flags POSIX e dados de fuso IANA; Windows não foi homologado e IO incompatível é recusado. Use um diretório confiável e isolado.

```sh
PYTHONPATH=src python3 -m camaleao_marketing examples/seo.json --output /tmp/seo-report.json
PYTHONPATH=src python3 -m camaleao_marketing examples/search-console.json --output /tmp/gsc-report.json
PYTHONPATH=src python3 -m camaleao_marketing examples/paid-media.json --output /tmp/ads-report.json
```

Os arquivos de saída precisam ser novos; o CLI recusa sobrescrita. Todos os exemplos são fictícios. No exemplo de mídia paga, gasto total BRL150,00; CPA Google BRL20,00 e Meta BRL25,00. Receita declarada é zero, e não existe ROAS combinado entre plataformas. Isso é aritmética de fixture, não resultado comercial.

Exports CSV nativos precisam ser normalizados pelo operador para [o contrato JSON](docs/CONTRACT.md), conferindo dimensões, filtros, moeda, período, definição de conversão e janela de atribuição. Não há importador universal ou conector homologado. Não anexar dados de leads/segredos nem versionar relatórios de clientes.

## Desenvolvimento e verificação

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Validação local: **38 testes do motor e oito testes independentes aprovados**. Três exemplos CLI executados. Inclui métricas, zero denominadores, limites, HTML não confiável, ausência de eco de texto bruto, chaves de autorização recusadas, erros genéricos, symlinks e criação sem sobrescrita. A CI executa unittest e os exemplos em Python 3.11/3.12; resultado remoto registrado na PR.

Isso não comprova qualidade gerativa, autenticidade de export, retorno de marketing, indexação, acesso a contas, isolamento multitenant ou produção. O ensaio de instruções por agente é distinto de homologação na conta ChatGPT por outro operador.

## Arquitetura e evolução

Entrada local → contrato/limites → observações/cálculos → relatório rastreável → interpretação/revisão humana. [ADR](docs/adr/0001-offline-first.md), [segurança](SECURITY.md), [contribuição](CONTRIBUTING.md), [atribuição](THIRD_PARTY_NOTICES.md).

Não duplicar `open-seo`, `no-ai-slop`, `camaleao-portal`, `radar-integration-hub` ou `radar-evidence-kit`. Integrações futuras dependem de seus contratos/autorização reais; não estão conectadas nesta versão. Próximo marco: um segundo operador executar os três casos no ChatGPT, conferir os cálculos e medir utilidade antes de usar dados reais consentidos ou criar conectores.

A [auditoria em 30 seções](https://github.com/ofelipepeixoto/camaleao-marketing-copilot/blob/docs/notfair-audit/docs/Relatorio-NotFair-2026-10-17.md) e evidências ficam numa PR independente. Ela registra a suíte upstream incompleta por bloqueio automático, divergência de versão e cinco observações de segurança. As falhas upstream não foram corrigidas por copiar este adaptador; seus scripts de rede/CMS não fazem parte do runtime.

Versão experimental para revisão humana. Sem merge, release estável, serviço hospedado, conexão paga ou produção nesta entrega. Licença [MIT original](LICENSE); [MIT upstream](third_party/notfair/LICENSE) preservada. Sem afiliação NotFair/OpenAI/Google/Meta.
