# Segurança e limites

Não anexar segredos, dados de leads ou conteúdo privado aos exemplos públicos. Relatórios locais podem revelar métricas comerciais: guardar fora do Git e aplicar retenção conforme a operação. Hash vincula conteúdo; não autentica export, usuário ou origem, nem impede inferência de dados previsíveis.

O núcleo aceita somente os schemas publicados, tamanho/quantidade limitados e arquivos locais. Não baixa URLs, não executa HTML/JavaScript e não envia dados a modelos ou plataformas. Saída é JSON e contém observações/propostas pending com execution_allowed=false. Isso não é autorização para um consumidor externo; ele precisa de identidade, escopo, aprovação vinculada à ação e verificação de resultado próprios.

Não é servidor multiusuário, sandbox de sistema operacional, redator universal de dados pessoais ou controle de acesso a todo o disco. Verificação de symlinks não prova resistência a corridas de arquivos. Executar em diretório isolado confiável; não usar como endpoint para uploads adversariais sem nova revisão.

Falhas de parsing e validação devem retornar erro genérico sem ecoar dados. Não registrar HTML bruto ou parâmetros com tokens. Ausência de dependências runtime de terceiros reduz a superfície de supply chain, mas não prova ausência de vulnerabilidades; manter Python atualizado.

Para relatar um problema, iniciar contato privado pelo responsável do repositório. Não abrir issue pública com dados de clientes ou segredos. Não há SLA nem programa de recompensa anunciado. Rollback: descartar os relatórios experimentais e reverter a alteração; nenhuma migração/banco/campanha foi modificada.
