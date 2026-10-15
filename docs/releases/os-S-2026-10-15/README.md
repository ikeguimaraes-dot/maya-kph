# OS S · Maya · BLOQUEADO PARA DEPLOY

Esta proposta parte do main d92fc4d2f569580fb0758cd2ea26de6fe31ba60b. NÃO representa a fonte em produção.
Railway deployment 02935179-8a12-4e78-ad13-36964a1bb3c6 (09/10) não tem commitHash e contém proteções não presentes no repositório: webhook publicado já rejeita assinatura inválida com 403. Pessoas já usa MAYA_INTERNAL_TOKEN/Bearer e mantém chat pausado.

Patch preparado: RequestValidator, X-API-Key, claim MessageSid, takeover, role operator normalizada, salario_base → salario e retirada da tabela salarial fixa (a ferramenta já consulta vagas). Cinco testes locais passaram.

Não mesclar nem publicar este patch sem recuperar e reconciliar a fonte do deploy vigente e os chamadores Bearer: fazê-lo removeria proteções/fluxos posteriores. Não se afirma que salario_base ainda exista no serviço vigente.

Repositório segue público; ferramenta GitHub disponível não oferece alteração de visibilidade. Privacidade não foi concluída. Histórico antigo também contém a tabela salarial.
