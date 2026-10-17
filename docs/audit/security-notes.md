# Segurança — NotFair, inspeção somente leitura

Data: 2026-10-17. Alvo: `nowork-studio/notfair-plugin`, commit `c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d`.

## Escopo e limites

Lidos `AGENTS.md`, `docs/plugin-development.md`, `docs/safety.md`, `docs/mcp-connection.md`, `SECURITY.md`, manifests, scripts de rede/CMS, script do calendário, atualização/configuração e testes de fronteira existentes. Skill Sênior Global de Cibersegurança aplicada com referências 01, 02 e 14. O upstream não foi alterado. Não executei instalação, integração real, chamadas pagas ou requisições de teste para fora do processo. Testes adicionais usam dados fictícios e mocks; `socket.socket.connect` foi bloqueado para todos os destinos, inclusive loopback.

As cinco observações abaixo foram reproduzidas por `security_reproductions.py`; **5 testes aprovados significa que os comportamentos problemáticos foram observados**, não que foram corrigidos. Log: `security_reproductions.log`.

## Achados confirmados

### NF-SEC-01 — Seleção de credenciais pode trocar o cliente/projeto (média)

- Componente/evidência: `seo/seo-analysis/scripts/push_strapi_seo.py:122-134`, em especial `for name in (".env.local", ".env")` e `env.update(...)`. Cada diretório ancestral sobrescreve os valores do diretório atual; dentro de cada pasta `.env` sobrescreve `.env.local`.
- Reprodução: pasta `client-a/.env.local` com URL/chave fictícias A e `.env` na pasta mãe com B. `find_and_load_env()` retorna B. Variáveis explícitas de ambiente ainda têm precedência em `get_config()`; o achado exige ausência dessas variáveis.
- Impacto: análises ou publicação podem ocorrer no site de outro cliente quando há configuração compartilhada em pastas superiores. É uma falha de seleção local do alvo, não quebra remota de autenticação.
- Mesmo padrão estático: `fetch_wordpress_content.py:100-107`, `preflight_wordpress.py:53-60`, `fetch_strapi_content.py:103-110`, `preflight_strapi.py:48-55`, `fetch_ghost_content.py:66-78`, `preflight_ghost.py:52-59`, `fetch_contentful_content.py:59-66`, `preflight_contentful.py:49-56`, `cms_detect.py:36-43`.
- Correção: carregar ancestral antes do projeto, `.env` antes de `.env.local`, definir raiz explícita e mostrar o alvo selecionado sem segredo antes de qualquer escrita. Melhor: não descobrir credenciais em diretórios de outro projeto.
- Aceitação: teste com duas pastas/duas contas; nenhuma mudança de alvo por configuração ancestral.

### NF-SEC-02 — Guard de concorrência Strapi falha aberto se a leitura atual falhar (média)

- Evidência: `push_strapi_seo.py:220-228` captura erro e retorna dois dicionários vazios. `:356-359` só verifica divergência se ambos os timestamps existirem; `:369-370` aceita o item e `:398-399` escreve após aprovação.
- Reprodução: GET atual lança `URLError`, lote contém `updated_at`, `process_updates(..., version_hint="5", auto_yes=True)` chama PUT mesmo assim. A opção `auto_yes` é a CLI existente; não há bypass de controle do serviço nesta reprodução.
- Condição: usuário/automação já autorizou o lote e servidor permite escrita; leitura pode falhar por rede/permissão. O problema é descartar a precondição da escrita.
- Impacto: atualização com valores atuais e esquema desconhecidos; risco de sobrescrever alteração concorrente. A janela GET→PUT também continua sujeita a corrida mesmo com timestamps obtidos.
- Correção: falhar fechado na leitura ou no timestamp obrigatório; usar condição atômica de versão/ETag se suportada; nunca interpretar leitura indisponível como campo vazio.
- Aceitação: falha do GET e timestamp ausente produzem zero PUT; versão divergente também; caso positivo permanece.

### NF-SEC-03 — Ghost não aplica fronteira de rede a redirects/conexão (média, exposição condicionada)

- Evidência: `fetch_ghost_content.py:102-127` verifica DNS antecipadamente; `:139` e `:177` usam `urllib.request.urlopen` padrão. `preflight_ghost.py:89-119`, `:132` repete o desenho. Falha de resolução é ignorada.
- Reprodução sem rede: validação aceita DNS público fictício e o handler padrão usado pelo transporte aceita redirect da origem pública a `http://127.0.0.1:8765/internal` sem novo guard. O código não instala handler para revalidar esse salto. Não houve exploração de serviço local nem prova de exfiltração.
- Condições: Ghost configurado/comprometido redireciona, ou hostname controlado muda resolução entre preflight e conexão. WP/Strapi têm bloqueio same-origin para Authorization, mas seu DNS é também validado só antecipadamente; o achado de redirect aqui é específico do Ghost.
- Impacto: requisição GET pode alcançar serviços internos/metadados pela máquina do operador. Chave Ghost fica em query string por contrato da API; não afirmar que urllib a encaminha automaticamente a todo redirect — o Location determina a URL nova.
- Correção: reaproveitar transporte público com DNS validado/pinado em toda conexão, redirects limitados à origem, HTTPS e política explícita sobre proxies. Para CMS interno legitimamente necessário, criar modo separado e allowlist do operador, jamais relaxar silenciosamente.
- Aceitação: IPs privados/mistos/DNS rebind/redirects e downgrade recusados antes de conectar; origem pública normal continua funcionando.

### NF-SEC-04 — Limite de páginas não limita corpo nem requisições de links (média)

- Evidência: `seo/broken-link-checker/scripts/checker.py:157` e `:199` chamam `response.read()` sem tamanho; `:203-205` agenda um Future para cada link encontrado, inclusive externos; só cinco workers concorrentes, porém fila ilimitada; `max_pages` só controla `:172`.
- Reprodução: HTML sintético de uma única página com 120 links, `max_pages=1`, produziu 120 chamadas `check_url`; leitura foi `read(-1)`. Não foram usados corpos enormes nem 120 conexões reais.
- Impacto: consumo de memória/tempo e volume de requisições podem crescer com conteúdo controlado por terceiro. Timeout de socket não é deadline global; servidor pode manter stream lento. `max_pages` não é quota total.
- Correção: tamanho máximo por resposta e agregado, teto total de requisições/links/URLs únicos, fila limitada, cancelamento/deadline global e limite de redirects. Separar crawl interno de checagem externa optativa.
- Aceitação: fixture que excede cada teto deve parar com motivo auditável, sem despachar além da quota.

### NF-SEC-05 — Identificadores do lote Strapi entram no caminho sem validação (média; impacto final depende de backend/proxy)

- Evidência: `push_strapi_seo.py:343`, `:391-396` interpola `document_id`/`id` diretamente no path; `:443-449` só verifica que o lote é lista. `content_type` também vem de configuração/CLI sem validação de segmento.
- Reprodução: ID fictício `../users/7?other=1` fez o helper receber PUT para `/api/articles/../users/7?other=1`, não um único segmento de documento. Nenhum servidor foi chamado; normalização de `..`, route de destino, permissões e efeito real não foram demonstrados.
- Impacto: dados de lote podem alterar rota/query de uma chamada privilegiada; risco de atuar fora da coleção/documento revisado. Não se trata de alteração de host por `urljoin` (o código concatena strings), nem prova de escalonamento de privilégios.
- Correção: schema estrito por versão; ID v4 inteiro positivo e documentId v5 alfanumérico com tamanho limitado; content type allowlist; rejeitar `/`, `?`, `#`, `%` e tipos inesperados; construir segmentos codificados somente após validação.
- Aceitação: ID malformado deve falhar antes de qualquer GET/PUT; lote inteiro validado antes de primeira operação.

## Riscos adicionais por inspeção, sem exploração

- **HTTP com segredo aceito**: validadores de CMS aceitam `http` além de `https` (`push_strapi_seo.py:79`, Ghost`:108`), enquanto `_headers` envia Bearer e Ghost usa chave na query. Operador pode enviar credencial sem TLS se configurar URL pública HTTP; exigir HTTPS no perfil de produção. Isso depende da configuração, não foi observado com credenciais reais.
- **Calendário**: `scripts/notfair-content-calendar.py:374-375` diz “loopback only” mas `:396` aceita `--host` arbitrário. `/calendar.json` (`:332-340`) não tem autenticação. Padrão `127.0.0.1` é adequado ao uso local; `--host 0.0.0.0` expõe dados na interface configurada. Não testei acesso externo. Restringir bind a loopback ou fornecer autenticação/reverse proxy apropriado para compartilhamento.
- **Dependências**: `requirements.txt:1-3` e `requirements-test.txt` têm apenas pisos de versão, sem lock/hash. Portanto ambientes não são reprodutíveis e uma instalação futura pode mudar transitivos. A presença de Dependabot é positiva, mas não prova ausência de CVEs. Não consultei advisories ou instalei dependências nesta subtarefa; **nenhuma lista de CVEs está confirmada por mim**.
- **Estado legado**: scripts de config/updates/change-watch ainda usam `~/.toprank` e variáveis `TOPRANK_*`, apesar de docs orientarem `.notfair`. Isso indica deriva operacional; não é por si só vulnerabilidade. O watcher imprime campos do change-log direto no contexto da sessão, sem delimitá-los como dados; docs gerais já dizem tratar retornos como não confiáveis. Não chamar isso de execução automática confirmada de prompt injection.
- **Busca limitada de segredos**: padrões de chaves privadas/AWS/GitHub/OpenAI/Google no checkout (sem testes/changelog) não tiveram correspondência. Não é varredura completa de histórico, credenciais fora de padrões ou dependências.

## Controles positivos verificados no código

1. Crawler: `_public_connection` resolve uma vez, valida todas as respostas DNS, normaliza IPv4-mapped IPv6 e conecta nos endereços examinados (`checker.py:36-69`). Proxies desabilitados; HTTP/S apenas e credenciais de URL recusadas; redirect passa por validação e novo transporte público (`:86-96`). Não confundir com a lacuna Ghost.
2. WP/Strapi: `_http.py:15-24` recusa redirect de Authorization para outra origem, inclusive downgrade, porta e credenciais diferentes; testes existentes exercitam múltiplos redirects.
3. `_uid.py:79-104`: escrita JSON em tempfile, modo 0600 quando suportado, replace atômico; evita seguir symlink no arquivo de destino. Diretório pai ainda é fronteira do operador e Windows pode não honrar modo POSIX.
4. Calendário usa `html.escape` em campos renderizados; testes existentes incluem payloads HTML; não foi encontrado XSS confirmado nessa renderização inspecionada.
5. Regras explícitas de mudança exata/limite de autorização e conteúdo não confiável em `docs/safety.md`; boa referência para a adaptação. São instruções ao agente, não prova de autorização aplicada no servidor.
6. Registry CI usa SHA de checkout e checksum do publisher, permissões `contents:read`/`id-token:write` específicas. Publicação é efeito real e não deve ser herdada numa cópia Radar sem revisar namespace/alvo e desativar o workflow.

## MCP, licença e reutilização ChatGPT

- Todos os manifests apontam um MCP HTTPS OAuth externo (`https://notfair.co/api/mcp/notfair`). `docs/plugin-development.md` declara o servidor privado. Não há implementação pública do servidor para auditar validação, autorização por objeto/tenant, escopos OAuth, armazenamento de tokens, rate limits, auditoria, confirmação de writes, revogação ou custos. São **não verificados**, não falhas confirmadas.
- No ChatGPT, importar texto das skills não cria ferramentas, conexões ou autorização. Uma adaptação útil pode gerar planos, diagnósticos de exports fictícios e propostas revisáveis. Ações reais devem usar conectores efetivamente disponíveis, conta/propriedade confirmada e controles de aprovação do host/servidor.
- Boa extração: taxonomia de intenção/roteamento, métricas e fórmulas de campanhas, planos de experimento, contratos de evidência, antes/depois e rollback, schemas de proposta e testes de conteúdo não confiável. Priorizar isso antes de ligar MCP com capacidade de gasto/publicação.
- Fonte do plugin usa **MIT**, `LICENSE:3` copyright **2026 Toprank Contributors**; manter licença/atribuição em cópia ou porção substancial. Não reatribuir material copiado como exclusivamente autoral do Radar. MIT do checkout não demonstra licença do SaaS, marcas, dados das plataformas, anúncios/clientes ou direitos de acesso às APIs.
- Não há pesos de modelo distribuídos neste escopo. A skill Gemini depende de CLI e credencial externa; não usar na auditoria, nem interpretar disponibilidade do wrapper como chamada validada.

## Prioridades sugeridas

P0 antes de qualquer uso real: selecionar explicitamente conta/site e credencial; impedir writes da adaptação por padrão; revisão humana da proposta exata.

P1 correções locais isoladas: precedência de configuração; fail-closed e validação de lote Strapi; fronteira de rede Ghost; quotas de corpo/requisições do crawler. Cada correção deve ter teste de falha antes/depois e compatibilidade positiva.

P2 homologação separada: dependências travadas e advisories, contrato MCP read-only, OAuth real em conta de teste, duas contas/tenants, logs mascarados, revogação e teste de rollback. Custo/produção continuam fora desta subtarefa.
