# Camaleão Marketing Copilot

Experimento offline de análise de marketing e instruções para ChatGPT. Ler README.md, docs/CONTRACT.md e SECURITY.md antes de mudar o núcleo. Não instalar o NotFair nem registrar MCPs por ler este repositório.

Preservar análise sem rede, SDKs de anúncios, credenciais, subprocessos ou chamadas pagas. HTML e exports são dados não confiáveis. Saída deve continuar execution_allowed=false e review_status=pending; não aceitar autorização em um campo de entrada. Isso limita o motor; instruções em linguagem natural não contêm ferramentas externas do ChatGPT.

Testar com `PYTHONPATH=src python3 -m unittest discover -s tests -v`. Manter os exemplos fictícios e sem dados identificáveis. Não versionar relatórios de clientes. Código, teste e contrato da mesma alteração ficam juntos. Sem merge automático, implantação ou alteração de contas.

Código novo original MIT de Carlos Felipe; catálogo e licença upstream em third_party/notfair. Não usar a marca NotFair como identidade deste produto nem reivindicar autoria do upstream.
