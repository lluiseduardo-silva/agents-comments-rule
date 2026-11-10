using System;
using System.Collections.Generic;

namespace ControleEstoque
{
    /// <summary>
    /// Par imutável de sku e quantidade, usado como item de uma reserva e como linha de um <see cref="Pedido"/>.
    /// </summary>
    public sealed class ItemPedido
    {
        /// <summary>
        /// Cria um item com o sku e a quantidade informados.
        /// </summary>
        /// <param name="sku">
        /// Identificador do produto. Não pode ser nulo; texto vazio é aceito e tratado como um sku qualquer.
        /// </param>
        /// <param name="quantidade">
        /// Unidades do sku. Nenhuma faixa é verificada aqui; <see cref="Estoque.Reservar"/> recusa valores menores
        /// ou iguais a zero.
        /// </param>
        /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
        public ItemPedido(string sku, int quantidade)
        {
            if (sku == null)
            {
                throw new ArgumentNullException(nameof(sku));
            }

            Sku = sku;
            Quantidade = quantidade;
        }

        /// <summary>Identificador do produto; nunca nulo.</summary>
        public string Sku { get; }

        /// <summary>Unidades do sku; pode ser zero ou negativa, porque o construtor não verifica a faixa.</summary>
        public int Quantidade { get; }
    }

    /// <summary>
    /// Pedido mutável que acumula em <see cref="Linhas"/> os itens reservados para ele.
    /// </summary>
    public sealed class Pedido
    {
        /// <summary>
        /// Linhas do pedido, na ordem em que foram acrescentadas; a lista nunca é nula e começa vazia.
        /// </summary>
        public List<ItemPedido> Linhas { get; } = new List<ItemPedido>();
    }

    /// <summary>
    /// Erro de quantidade inválida: ocorre quando uma reposição ou uma reserva recebe quantidade menor ou igual a
    /// zero.
    /// </summary>
    public sealed class QuantidadeInvalidaException : Exception
    {
        /// <summary>
        /// Cria o erro para o sku e a quantidade recusada.
        /// </summary>
        /// <param name="sku">Sku ao qual a quantidade se refere; armazenado sem validação.</param>
        /// <param name="quantidade">Quantidade recusada; armazenada sem validação.</param>
        public QuantidadeInvalidaException(string sku, int quantidade)
            : base($"Quantidade inválida para o sku '{sku}': {quantidade}. A quantidade deve ser maior que zero.")
        {
            Sku = sku;
            Quantidade = quantidade;
        }

        /// <summary>Sku ao qual a quantidade recusada se refere.</summary>
        public string Sku { get; }

        /// <summary>Quantidade recusada.</summary>
        public int Quantidade { get; }
    }

    /// <summary>
    /// Erro de estoque insuficiente: ocorre quando uma reserva pede mais unidades de um sku do que o saldo
    /// disponível, inclusive quando o sku não existe no estoque.
    /// </summary>
    public sealed class EstoqueInsuficienteException : Exception
    {
        /// <summary>
        /// Cria o erro para o sku, a quantidade pedida e o saldo disponível.
        /// </summary>
        /// <param name="sku">Sku cujo saldo é insuficiente; armazenado sem validação.</param>
        /// <param name="solicitado">Unidades pedidas na reserva; armazenadas sem validação.</param>
        /// <param name="disponivel">Saldo do sku no momento da recusa, em unidades; armazenado sem validação.</param>
        public EstoqueInsuficienteException(string sku, int solicitado, int disponivel)
            : base($"Estoque insuficiente para o sku '{sku}': solicitado {solicitado}, disponível {disponivel}.")
        {
            Sku = sku;
            Solicitado = solicitado;
            Disponivel = disponivel;
        }

        /// <summary>Sku cujo saldo é insuficiente.</summary>
        public string Sku { get; }

        /// <summary>Unidades pedidas na reserva.</summary>
        public int Solicitado { get; }

        /// <summary>Saldo do sku no momento da recusa; zero quando o sku não existe no estoque.</summary>
        public int Disponivel { get; }
    }

    /// <summary>
    /// Erro de limite excedido: ocorre quando uma reposição levaria o saldo de um sku acima do limite por sku do
    /// estoque.
    /// </summary>
    public sealed class LimiteExcedidoException : Exception
    {
        /// <summary>
        /// Cria o erro para o sku, o saldo atual, a quantidade recusada e o limite do estoque.
        /// </summary>
        /// <param name="sku">Sku cuja reposição é recusada; armazenado sem validação.</param>
        /// <param name="saldo">Saldo do sku antes da reposição, em unidades; armazenado sem validação.</param>
        /// <param name="quantidade">Unidades que a reposição somaria; armazenadas sem validação.</param>
        /// <param name="limite">Saldo máximo permitido por sku, em unidades; armazenado sem validação.</param>
        public LimiteExcedidoException(string sku, int saldo, int quantidade, int limite)
            : base($"Limite excedido para o sku '{sku}': saldo {saldo} mais {quantidade} ultrapassa o limite {limite}.")
        {
            Sku = sku;
            Saldo = saldo;
            Quantidade = quantidade;
            Limite = limite;
        }

        /// <summary>Sku cuja reposição é recusada.</summary>
        public string Sku { get; }

        /// <summary>Saldo do sku antes da reposição; a recusa o mantém inalterado.</summary>
        public int Saldo { get; }

        /// <summary>Unidades que a reposição somaria.</summary>
        public int Quantidade { get; }

        /// <summary>Saldo máximo permitido por sku no estoque.</summary>
        public int Limite { get; }
    }

    /// <summary>
    /// Controle de estoque em memória que mantém o saldo de cada sku entre zero e um limite por sku fixado na
    /// criação.
    /// </summary>
    /// <remarks>
    /// Os skus são comparados de forma ordinal, diferenciando maiúsculas de minúsculas, e nenhum método de instância
    /// os normaliza. A instância não é sincronizada: o uso por mais de uma thread exige sincronização externa.
    /// </remarks>
    public sealed class Estoque
    {
        /// <summary>
        /// Saldo de cada sku reposto ao menos uma vez; todo valor fica entre zero e <see cref="_limitePorSku"/>.
        /// </summary>
        private readonly Dictionary<string, int> _saldos = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Saldo máximo permitido para cada sku, em unidades; sempre maior que zero.</summary>
        private readonly int _limitePorSku;

        /// <summary>
        /// Cria um estoque vazio, em que todo sku tem saldo zero.
        /// </summary>
        /// <param name="limitePorSku">
        /// Saldo máximo que cada sku pode atingir, em unidades; deve ser maior que zero.
        /// </param>
        /// <exception cref="ArgumentOutOfRangeException">
        /// Se <paramref name="limitePorSku"/> for menor ou igual a zero.
        /// </exception>
        public Estoque(int limitePorSku)
        {
            if (limitePorSku <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(limitePorSku), limitePorSku, "O limite por sku deve ser maior que zero.");
            }

            _limitePorSku = limitePorSku;
        }

        /// <summary>
        /// Soma <paramref name="quantidade"/> ao saldo de <paramref name="sku"/>.
        /// </summary>
        /// <remarks>
        /// Modifica o estado da instância: o saldo do sku aumenta em <paramref name="quantidade"/> unidades. Não
        /// modifica seus argumentos. Quando lança exceção, nenhum saldo é alterado.
        /// </remarks>
        /// <param name="sku">
        /// Identificador do produto. Não pode ser nulo; texto vazio é aceito e tratado como um sku qualquer. Um sku
        /// que não existe no estoque parte do saldo zero.
        /// </param>
        /// <param name="quantidade">Unidades a somar; deve ser maior que zero.</param>
        /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
        /// <exception cref="QuantidadeInvalidaException">
        /// Se <paramref name="quantidade"/> for menor ou igual a zero.
        /// </exception>
        /// <exception cref="LimiteExcedidoException">
        /// Se o saldo resultante ultrapassar o limite por sku definido na criação do estoque.
        /// </exception>
        public void Repor(string sku, int quantidade)
        {
            if (sku == null)
            {
                throw new ArgumentNullException(nameof(sku));
            }

            if (quantidade <= 0)
            {
                throw new QuantidadeInvalidaException(sku, quantidade);
            }

            _saldos.TryGetValue(sku, out int saldoAtual);

            // A comparação por subtração não estoura int, ao contrário de saldoAtual + quantidade; saldoAtual
            // nunca excede _limitePorSku.
            if (quantidade > _limitePorSku - saldoAtual)
            {
                throw new LimiteExcedidoException(sku, saldoAtual, quantidade, _limitePorSku);
            }

            _saldos[sku] = saldoAtual + quantidade;
        }

        /// <summary>
        /// Devolve o saldo atual de <paramref name="sku"/>.
        /// </summary>
        /// <remarks>
        /// Não modifica seu argumento nem o estado da instância.
        /// </remarks>
        /// <param name="sku">
        /// Identificador do produto. Não pode ser nulo; texto vazio é aceito e tratado como um sku qualquer.
        /// </param>
        /// <returns>
        /// Saldo do sku, em unidades, entre zero e o limite por sku. Zero quando o sku não existe no estoque ou
        /// quando todo o seu saldo está reservado.
        /// </returns>
        /// <exception cref="ArgumentNullException">Se <paramref name="sku"/> for nulo.</exception>
        public int Quantidade(string sku)
        {
            if (sku == null)
            {
                throw new ArgumentNullException(nameof(sku));
            }

            _saldos.TryGetValue(sku, out int saldo);
            return saldo;
        }

        /// <summary>
        /// Reserva os itens para o pedido: para cada item, na ordem da lista, debita a quantidade do saldo do sku e
        /// acrescenta o item ao final de <see cref="Pedido.Linhas"/>.
        /// </summary>
        /// <remarks>
        /// Modifica o estado da instância (os saldos debitados) e modifica <paramref name="pedido"/> (os itens
        /// acrescentados a <see cref="Pedido.Linhas"/>). Não modifica os itens em si. A operação não é atômica: ela
        /// para no primeiro item que falha, e os itens anteriores a ele continuam debitados do saldo e presentes em
        /// <see cref="Pedido.Linhas"/>; o item que falha e os seguintes não alteram nada. Quando
        /// <see cref="ArgumentNullException"/> é lançada, nada é alterado.
        /// </remarks>
        /// <param name="itens">
        /// Itens a reservar. Não pode ser nulo nem conter elementos nulos; lista vazia é aceita e não altera nada. O
        /// mesmo sku pode aparecer em mais de um item, e cada ocorrência é debitada em separado. Pode ser a própria
        /// lista <see cref="Pedido.Linhas"/> de <paramref name="pedido"/>: nesse caso são processados apenas os
        /// itens presentes no início da chamada.
        /// </param>
        /// <param name="pedido">
        /// Pedido que recebe os itens reservados; não pode ser nulo. As linhas que ele contém são preservadas.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Se <paramref name="itens"/> ou <paramref name="pedido"/> for nulo.
        /// </exception>
        /// <exception cref="ArgumentException">Se um elemento de <paramref name="itens"/> for nulo.</exception>
        /// <exception cref="QuantidadeInvalidaException">
        /// Se a quantidade de um item for menor ou igual a zero.
        /// </exception>
        /// <exception cref="EstoqueInsuficienteException">
        /// Se a quantidade de um item for maior que o saldo do seu sku no momento em que o item é processado,
        /// inclusive quando o sku não existe no estoque.
        /// </exception>
        public void Reservar(IReadOnlyList<ItemPedido> itens, Pedido pedido)
        {
            if (itens == null)
            {
                throw new ArgumentNullException(nameof(itens));
            }

            if (pedido == null)
            {
                throw new ArgumentNullException(nameof(pedido));
            }

            // O total é lido antes do laço porque itens pode ser a própria pedido.Linhas, que cresce a cada
            // iteração.
            int total = itens.Count;
            for (int indice = 0; indice < total; indice++)
            {
                ItemPedido item = itens[indice];
                if (item == null)
                {
                    throw new ArgumentException($"O item na posição {indice} é nulo.", nameof(itens));
                }

                if (item.Quantidade <= 0)
                {
                    throw new QuantidadeInvalidaException(item.Sku, item.Quantidade);
                }

                _saldos.TryGetValue(item.Sku, out int saldoAtual);
                if (item.Quantidade > saldoAtual)
                {
                    throw new EstoqueInsuficienteException(item.Sku, item.Quantidade, saldoAtual);
                }

                _saldos[item.Sku] = saldoAtual - item.Quantidade;
                pedido.Linhas.Add(item);
            }
        }

        /// <summary>
        /// Normaliza os skus da lista: tira os espaços em branco das pontas de cada texto, converte-o para
        /// maiúsculas pela cultura invariante e remove da lista os que ficarem vazios.
        /// </summary>
        /// <remarks>
        /// Modifica <paramref name="skus"/> in-place: cada elemento mantido é sobrescrito pela sua forma
        /// normalizada, na mesma ordem relativa, e os vazios são removidos, o que reduz o tamanho da lista. Não lê
        /// nem modifica o estado de nenhuma instância de <see cref="Estoque"/>. Quando lança exceção, a lista não é
        /// alterada.
        /// </remarks>
        /// <param name="skus">
        /// Lista a normalizar; não pode ser nula. Lista vazia é aceita. Elementos nulos são tratados como texto
        /// vazio e removidos.
        /// </param>
        /// <returns>Quantidade de elementos removidos da lista; zero quando nenhum ficou vazio.</returns>
        /// <exception cref="ArgumentNullException">Se <paramref name="skus"/> for nula.</exception>
        public static int NormalizarSkus(List<string> skus)
        {
            if (skus == null)
            {
                throw new ArgumentNullException(nameof(skus));
            }

            int mantidos = 0;
            for (int indice = 0; indice < skus.Count; indice++)
            {
                string sku = skus[indice];
                string normalizado = sku == null ? string.Empty : sku.Trim().ToUpperInvariant();
                if (normalizado.Length > 0)
                {
                    skus[mantidos] = normalizado;
                    mantidos++;
                }
            }

            int removidos = skus.Count - mantidos;
            skus.RemoveRange(mantidos, removidos);
            return removidos;
        }
    }
}
