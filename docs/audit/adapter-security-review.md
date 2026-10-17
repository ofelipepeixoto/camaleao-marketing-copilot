# Revisão independente do adaptador Camaleão Marketing Copilot

Data: 2026-10-17. Revisão somente leitura de `src/camaleao_marketing` e instruções/contratos do novo projeto. Não executei os scripts upstream nem conectores e não alterei o adaptador.

Versão revista: `core.py` SHA-256 `b0e97e39212dde78671b3add4f8ebb76c3c3caae9917345443675ef98f56a99c`.

## Resultado

**Nenhum bloqueador confirmado permanece no escopo offline inspecionado.** O resultado não homologa integrações, receitas, contas, uso multiusuário ou produção.

Foram detectados e comunicados ao autor dois problemas durante a revisão, corrigidos antes da validação final:

1. `HTMLParser` fornece `None` para atributos sem valor; `.lower()`/`.strip()` podiam receber `None`. A normalização em `_PageParser.handle_starttag` agora converte esses valores para string vazia. Cinco snapshots com `meta name`, `link rel`, `script type` e `content` sem valor foram processados com `review_status=pending`.
2. As garantias de IO dependem de flags POSIX. `_parent_fd` agora recusa plataforma/flags incompatíveis por `InputError`, evitando alegar suporte IO portátil. O motor `analyze(bytes)` continua independente dos caminhos de arquivos.

## Testes independentes

`adapter-security-review.py`: **8 testes aprovados**, com múltiplos subcasos; log `adapter-security-review.log`. Todos os sockets foram bloqueados, inclusive loopback. Cobertura:

- HTML com atributos sem valor;
- campos que tentam introduzir aprovação/execução;
- tipos trocados em esquema, contexto, modo e campos de mídia paga;
- marcador fictício privado no HTML e identificadores, ausente do relatório;
- hash vinculado aos bytes exatos;
- denominadores zero e métricas separadas por canal;
- criação sem sobrescrita e modo 0600;
- recusa a symlink no arquivo e diretório pai;
- limites de bytes e quantidade de linhas.

Os testes não instalam dependências. O motor usa biblioteca padrão. Os resultados são distintos dos testes upstream e não devem ser somados como validação de integração.

## Controles e métricas revistos

- JSON bruto limitado a 1 MiB, HTML a 256 KiB, linhas a 5.000 e saída de achados a 100; duplicatas de chaves, NaN/Infinity literais, floats no contrato e profundidade excessiva recusados.
- Inteiros não aceitam bool; valores monetários são strings decimais de duas casas e cálculos usam Decimal com precisão definida.
- CTR usa cliques/impressões; CPA usa gasto/conversões e ROAS receita/gasto dentro de cada canal; zero retorna indisponível. Receita/conversões não são somadas como vendas únicas entre plataformas.
- Sem requisições HTTP, subprocess, execução HTML/JavaScript, LLM, credenciais, publicação ou efeito em campanhas.
- Saída omite texto do HTML, consultas, URL, IDs/campanhas e project_id; inclui métricas, códigos, ponteiros, hash e contexto validado de medição. Datas/moeda/fuso/atribuição declarados não são prova de origem ou tracking.
- IO percorre diretórios por handles no-follow, lê somente arquivos regulares, limita bytes e cria relatório novo com exclusividade. Não é sandbox do disco, autenticação ou resistência universal a corrida em diretórios adversariais.
- `execution_allowed=false` e `review_status=pending` são declarações do artefato; nenhum consumidor externo deve usá-las como autorização real.

## Limites residuais

O parser é observação sintática de snapshot, sem DOM renderizado, HTTP, robots.txt, status de indexação, validade de rich results ou visibilidade em mecanismos de IA. Exports são autodeclarados, podem estar incompletos/duplicados e não têm autenticidade comprovada. `data_as_of` não estabelece atualização real. Recomendado manter os limites explicitados em docs/CONTRACT e SECURITY, testar com outro operador e tratar qualquer futuro conector como nova fronteira de segurança.
