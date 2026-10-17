# Reproduzir a auditoria

Fonte: nowork-studio/notfair-plugin commit c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d. `baseline-inventory.md` contém os comandos executados. Logs com `<WORKSPACE>` tiveram o prefixo local e espaços finais de linhas normalizados para publicação; não são logs completos de conta real.

`security_reproductions.py` contém cinco observações sintéticas sobre o upstream, não correções. Após obter um checkout do commit fixado em diretório isolado confiável:

```sh
python3 docs/audit/security_reproductions.py /path/to/notfair-upstream
```

O script bloqueia conexões Python e simula transportes; não executar contra um CMS ou conta real. Cinco testes aprovados significam **comportamentos problemáticos reproduzidos**, não segurança aprovada. Ele carrega módulos do checkout indicado; revisar o código antes e não apontar para checkout desconhecido.

Não repetir a suíte unitária original sem corrigir antes os mocks de rede/credenciais apontados em baseline-inventory.md. Essa suíte ficou incompleta por rejeição automática registrada em unit-blocked.txt. Contratos MCP estáticos foram executados sem OAuth live; quatro checks resultaram em três aprovados e uma falha por versão, com dois cenários live ignorados.

Os testes novos de `tests/` verificam o adaptador original. Não são substitutos dos E2Es de agentes, marketing real, OAuth ou homologação humana no ChatGPT. O catálogo de 48 referências upstream não foi executado nem instalado.

Para os oito testes independentes do adaptador, disponibilizar a branch de implementação e executar:

```sh
python3 docs/audit/adapter-security-review.py /path/to/camaleao-marketing-copilot
```

A PR de auditoria é independente e não contém o runtime. Apontar para checkout da branch feat/offline-chatgpt; nenhum teste dispara conectores reais.
