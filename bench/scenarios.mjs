// Definição do benchmark da rule de comentários: linguagens, cenários, tarefas, o que
// cada declaração-alvo deveria documentar e os tokens plantados para medir vazamento.

export const LANGS = {
  kotlin: { name: 'Kotlin', erroCupom: '`CupomInvalidoException`' },
  rust: { name: 'Rust', erroCupom: '`ErroCupom` (acrescente as variantes necessárias)' },
  typescript: { name: 'TypeScript', erroCupom: '`CupomInvalidoError`' },
  python: { name: 'Python', erroCupom: '`CupomInvalidoError`' },
  go: { name: 'Go', erroCupom: '`ErrCupomInvalido`' },
  csharp: { name: 'C#', erroCupom: '`CupomInvalidoException`' },
};

const DIRETO = 'Mudança direta, já aprovada: faça agora, sem plano.';
const NOMES = 'Use os nomes acima, adaptados à convenção de nomes da linguagem.';

export const SCENARIOS = {
  // Código novo a partir de uma especificação, sem nenhuma história no pedido.
  // Mede se o contrato sai completo: parâmetros, retorno, erros, mutação, falha parcial.
  's1-greenfield': {
    files: {
      kotlin: 'Estoque.kt',
      rust: 'estoque.rs',
      typescript: 'estoque.ts',
      python: 'estoque.py',
      go: 'estoque.go',
      csharp: 'Estoque.cs',
    },
    seeded: false,
    task: (lang, file) => `${DIRETO}

Crie o arquivo \`${file}\` em ${LANGS[lang].name} com um controle de estoque em memória. Só a biblioteca padrão. Não crie testes nem outros arquivos.

- Tipo \`Estoque\`, criado com \`limitePorSku\` (inteiro; menor ou igual a zero é erro).
- \`repor(sku, quantidade)\`: soma a quantidade ao saldo do sku. Quantidade menor ou igual a zero é erro. Saldo resultante acima de \`limitePorSku\` é erro, e nesse caso o saldo não muda.
- \`quantidade(sku)\`: devolve o saldo atual do sku; zero se o sku não existir.
- \`reservar(itens, pedido)\`: \`itens\` é uma lista de {sku, quantidade}; \`pedido\` é um objeto mutável com uma lista \`linhas\`. Para cada item, na ordem: debita a quantidade do saldo e acrescenta o item em \`pedido.linhas\`. Quantidade menor ou igual a zero é erro de quantidade inválida. Saldo insuficiente é erro de estoque insuficiente. No primeiro erro a operação para; os itens anteriores continuam debitados e continuam em \`pedido.linhas\`.
- \`normalizarSkus(skus)\`: recebe uma lista mutável de textos e a altera no lugar: tira espaços das pontas, converte para maiúsculas e remove os que ficarem vazios. Devolve quantos foram removidos.

${NOMES}`,
    targets: [
      { name: 'Estoque', kind: 'type' },
      {
        name: 'construtor de Estoque',
        kind: 'constructor',
        params: ['limitePorSku'],
        returns: false,
        errors: ['limitePorSku menor ou igual a zero'],
        mutates: [],
        partial_failure: false,
      },
      {
        name: 'repor',
        kind: 'function',
        params: ['sku', 'quantidade'],
        returns: false,
        errors: ['quantidade menor ou igual a zero', 'saldo resultante acima de limitePorSku'],
        mutates: ['o saldo guardado no próprio Estoque'],
        partial_failure: false,
      },
      {
        name: 'quantidade',
        kind: 'function',
        params: ['sku'],
        returns: true,
        errors: [],
        mutates: [],
        partial_failure: false,
      },
      {
        name: 'reservar',
        kind: 'function',
        params: ['itens', 'pedido'],
        returns: false,
        errors: ['quantidade menor ou igual a zero', 'saldo insuficiente'],
        mutates: ['o saldo guardado no próprio Estoque', 'o argumento pedido (pedido.linhas)'],
        partial_failure: true,
      },
      {
        name: 'normalizarSkus',
        kind: 'function',
        params: ['skus'],
        returns: true,
        errors: [],
        mutates: ['o argumento skus, alterado no lugar'],
        partial_failure: false,
      },
    ],
    tokens: {},
  },

  // Correção em arquivo sem comentários, com um pedido carregado de história, nomes,
  // ticket e decisão de produto. Mede se essa história vaza para o código.
  's2-bugfix': {
    files: {
      kotlin: 'LicencaAccessValidator.kt',
      rust: 'licenca_access_validator.rs',
      typescript: 'licencaAccessValidator.ts',
      python: 'licenca_access_validator.py',
      go: 'licenca_access_validator.go',
      csharp: 'LicencaAccessValidator.cs',
    },
    seeded: true,
    task: (lang, file) => `${DIRETO} Edite \`${file}\`. Não crie testes nem outros arquivos.

Contexto (ticket LIC-482, passo D2 do plano PR9): hoje \`canUpload\` devolve true para admin, mas logo em seguida o \`LicenseUploadService.assertUploadAllowed\` derruba a chamada com 403 em \`assertFileOwner\`, porque o arquivo pertence a um titular e o admin não é titular. Nunca existiu upload por admin funcionando: era só uma promessa que terminava em erro e, a cada tentativa, deixava um objeto órfão no S3. Foi isso que causou o incidente de 14/10 que a Marina, do time de Risco, reportou. Na reunião de quinta o time de Produto decidiu que admin não envia licença; habilitar de verdade exigiria aceitar um \`onBehalfOfUserId\` explícito no confirm, o que daria ao admin o poder de aprovar a participação de um compositor. O caminho administrativo para destravar uma venda já existe e é auditado: \`manual-complete\`.

O que fazer:
1. \`canUpload\`: admin deixa de ser aceito. Só compositor da guia pode enviar.
2. Nova função \`canAccessAfterCancel(venda, userId)\`: para venda cancelada, admin e compositor da guia mantêm o acesso; o comprador perde.
3. Nova função \`requireUpload(venda, userId)\`: não devolve nada; falha com o erro \`UploadNaoPermitido\` (crie o tipo) quando \`canUpload\` for falso.

${NOMES}`,
    targets: [
      {
        name: 'canUpload',
        kind: 'function',
        params: ['venda', 'userId'],
        returns: true,
        errors: [],
        mutates: [],
        partial_failure: false,
      },
      {
        name: 'canAccessAfterCancel',
        kind: 'function',
        params: ['venda', 'userId'],
        returns: true,
        errors: [],
        mutates: [],
        partial_failure: false,
      },
      {
        name: 'requireUpload',
        kind: 'function',
        params: ['venda', 'userId'],
        returns: false,
        errors: ['UploadNaoPermitido quando canUpload é falso'],
        mutates: [],
        partial_failure: false,
      },
      { name: 'UploadNaoPermitido', kind: 'type' },
    ],
    tokens: {
      pedido: [
        'LIC-482', 'D2', 'PR9', 'Marina', 'Risco', 'Produto', '14/10', 'S3', '403', 'órfão',
        'reunião', 'incidente', 'promessa', 'assertFileOwner', 'LicenseUploadService',
        'assertUploadAllowed', 'manual-complete', 'onBehalfOfUserId', 'titular', 'auditado',
      ],
    },
  },

  // O mesmo cenário 2 com um pedido genérico de comentários no fim. É a pressão máxima
  // para a história do pedido ir parar no código. (Preenchido logo abaixo do objeto.)
  's4-bugfix-comentado': null,

  // Arquivo já infestado de comentários narrativos. Mede se o estilo existente é
  // imitado, se a narrativa da função alterada é removida e se o resto fica intacto.
  's3-infested': {
    files: {
      kotlin: 'CupomService.kt',
      rust: 'cupom_service.rs',
      typescript: 'cupomService.ts',
      python: 'cupom_service.py',
      go: 'cupom_service.go',
      csharp: 'CupomService.cs',
    },
    seeded: true,
    task: (lang, file) => `${DIRETO} Edite \`${file}\`. Não crie testes nem outros arquivos.

O suporte abriu o PAG-1342: um cliente aplicou cupom vencido e o total do pedido ficou negativo. A Renata, do time de Checkout, pediu duas mudanças:
1. \`aplicar\`: cupom expirado passa a falhar com ${LANGS[lang].erroCupom}; o mesmo cupom não pode ser aplicado duas vezes no mesmo pedido (mesmo erro); o total nunca fica abaixo de zero (trava em zero).
2. Nova função \`remover(pedido, codigo)\`: tira o código de \`cuponsAplicados\` e devolve se ele estava lá. Não mexe no total.

${NOMES}`,
    targets: [
      {
        name: 'aplicar',
        kind: 'function',
        params: ['pedido', 'cupom'],
        returns: false,
        errors: [
          'limite de cupons por pedido atingido',
          'cupom expirado',
          'cupom já aplicado neste pedido',
        ],
        mutates: ['o argumento pedido (total e cuponsAplicados)'],
        partial_failure: false,
      },
      {
        name: 'remover',
        kind: 'function',
        params: ['pedido', 'codigo'],
        returns: true,
        errors: [],
        mutates: ['o argumento pedido (cuponsAplicados)'],
        partial_failure: false,
      },
    ],
    tokens: {
      // história vinda do pedido desta tarefa
      pedido: ['PAG-1342', 'Renata', 'suporte'],
      // narrativa que estava na função alterada (`aplicar`): deveria sumir
      alterada: ['2291', 'Financeiro', 'Carla', 'novembro', '⚠', 'empilhar'],
      // narrativa em `totalDeCupons`, que a tarefa não toca: deveria ficar como está
      intocada: ['PAG-1203', 'Diego', 'Plataforma', 'março', 'loop manual'],
      // narrativa no comentário da classe
      classe: ['Black Friday', 'PAG-1187'],
    },
  },
};

{
  const base = SCENARIOS['s2-bugfix'];
  SCENARIOS['s4-bugfix-comentado'] = {
    ...base,
    seedFrom: 's2-bugfix',
    task: (lang, file) => `${base.task(lang, file)}\n\nDeixe o código bem comentado.`,
  };
}
