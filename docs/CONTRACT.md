# Contrato v1

CLI: `PYTHONPATH=src python3 -m camaleao_marketing INPUT.json --output NOVO.json`.
Python 3.11+ em Linux/POSIX com O_NOFOLLOW/O_DIRECTORY; CLI Windows não homologado e recusa plataforma sem essas flags. Sem pacote runtime externo. O ambiente deve ter dados IANA de fusos para o modo de mídia paga (Linux CI possui). Nenhum URL é requisitado. O CLI devolve erro genérico e código não zero para entrada inválida; não imprime conteúdo bruto no erro.

## Entrada

JSON UTF-8 de no máximo 1 MiB, objeto com chaves exatas:

| Campo | Regra |
| --- | --- |
| schema_version | `camaleao.marketing.input/v1` |
| mode | `seo_page`, `search_console` ou `paid_media` |
| context | `project_id`, `date_start`, `date_end`; campos adicionais de ads abaixo |
| page ou rows | somente `page` em seo_page; somente `rows` nos outros modos |

IDs são opacos alfanuméricos com `_` e `-`, até 64 caracteres. Datas são ISO `YYYY-MM-DD` canônicas e início não pode exceder fim. Campos desconhecidos, JSON duplicado, NaN/Infinity, Unicode inválido e profundidade excessiva são recusados. Não adicionar campos de aprovação ou credenciais.

### SEO de snapshot

`page` tem `url` e `html`. URL absoluta HTTPS, sem usuário/senha, query, fragmento, portas alternativas ou controle. É validação sintática: não comprova host público, titularidade nem acessibilidade. HTML estático até 256 KiB; usa HTMLParser, sem executar scripts ou renderizar. Campos ausentes/duplicados geram observações. JSON-LD analisado apenas como sintaxe JSON; não valida vocabulário Schema.org, rich results ou elegibilidade. canonical igual ao URL fornecido não comprova canonical live.

### Search Console

`rows`: 1–5.000 objetos com `query` (texto até 512), `page` (URL HTTPS), `clicks`, `impressions` (inteiros 0–10¹²; booleanos recusados) e `position` (decimal em string, 1–1.000). Cliques não podem exceder impressões. O operador deve normalizar um único export de consulta/página/período, sem misturar totais e detalhes. Não há importador CSV automático nem deduplicação factual do export.

Fórmulas: CTR = 100 × Σcliques/Σimpressões; posição = Σ(posição × impressões)/Σimpressões. Denominador zero => null. A triagem de oportunidades marca linhas com ao menos 100 impressões e CTR estritamente abaixo de 2%. É limiar escolhido para o experimento, não regra de ranking ou estimativa de tráfego recuperável.

### Mídia paga

Contexto exige também:

| Campo | Valores |
| --- | --- |
| currency | BRL, USD ou EUR |
| conversion_definition | purchase, lead, signup ou custom |
| attribution_window | 1d_click, 7d_click, 30d_click ou platform_reported |
| timezone | fuso IANA válido |
| data_as_of | UTC canônico `YYYY-MM-DDTHH:MM:SSZ` |

Cada linha tem exatamente `id`, `campaign` (IDs opacos), `channel`, `currency`, `spend`, `revenue`, `conversions`, `clicks`, `impressions`. `channel`: google_ads, meta_ads, linkedin_ads, tiktok_ads, amazon_ads ou other. IDs de linha únicos; moeda igual ao contexto. Montantes não negativos em strings com duas casas e até 12 dígitos inteiros; sem notação científica, vírgula decimal ou moeda no valor. Contadores inteiros com os limites GSC.

Normalizar uma definição/janela/fuso por arquivo antes de analisar. Arquivos incompatíveis devem permanecer separados; para `platform_reported`, a comparabilidade entre plataformas é não verificada. Um evento `custom` precisa de descrição externa fornecida ao revisor, sem presumir venda. São declarações do operador, não inspeção de tracking. Não há conversão cambial, ajuste de timezone dos eventos ou validação de completude pela data_as_of.

Métricas por canal: CTR = 100 × cliques/impressões; CPA = gasto/conversões; ROAS = receita declarada/gasto. Global: só gasto. Não há CPA/ROAS combinado entre canais nem deduplicação de conversões/receita. Denominador zero => null; nulo não indica aprovação nem retorno. Decimais são strings, arredondadas half-up; CPA em duas casas, razões e posição em seis.

## Saída e IO

Schema `camaleao.marketing.report/v1`, métricas observadas, findings limitados a 100 com `source_pointer`, limites declarados, hash SHA-256 dos **bytes exatos** de entrada, `review_status=pending` e `execution_allowed=false`. Não é um recibo nativo do Evidence Kit. Contém metadados de período/medição validados; omite IDs, URLs, queries, campanhas e HTML brutos. Não é garantia de anonimização: métricas e hash ainda podem ser sensíveis.

Saída é JSON local criado exclusivamente; arquivo existente não é sobrescrito. Entrada deve ser arquivo regular; symlinks finais ou em pais são recusados. Pais da saída precisam existir. O programa não é sandbox de filesystem ou serviço de upload resistente a corridas; operar em diretório isolado confiável.

Exemplos versionados são a referência executável: usar `examples/*.json` e testes como amostras. Para converter um export real, o operador precisa conferir suas dimensões, filtros, unidade e definições antes de montar esse contrato. Nenhum parser de CSV de plataforma foi homologado.
