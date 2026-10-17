# ADR 0001 — Arquivos e cálculos locais antes de conectores

Status: aceito para o experimento; produção não homologada.

Contexto: NotFair oferece 48 workflows e já suporta Codex. Seu MCP real é um serviço hospedado fora do código público. O ecossistema Camaleão já tem plugin SEO, portal editorial, revisão de fontes e infraestrutura de autorização.

Decisão: criar um adaptador pequeno para ChatGPT e um motor Python sem dependências runtime de terceiros. Trabalhar com snapshot HTML ou exports convertidos para um contrato explícito, sem rede, execução de comandos recebidos ou operações em contas. Preservar o catálogo upstream como referência por commit, sem distribuir instaladores ou scripts de CMS.

Alternativas: instalar o upstream original (não resolve uso offline independente); criar MCP próprio agora (amplia operação sem benefício nesta validação); acrescentar outra UI/CRM (duplica o portal); usar só um prompt (não garante limites nem fórmulas reproduzíveis).

Consequências: dados não são live; conversão de exports exige conferir dimensões e filtros; não há homologação de conta/receita, ranking ou retorno. Futuro consumidor deverá usar os contratos reais do Evidence Kit e Hub, por versão fixada, antes de publicar ou gastar. Esta entrega não integra esses serviços e não ativa n8n.
