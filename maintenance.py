import sys
import subprocess
from config import produtos_collection, vendas_collection

def limpar_banco():
    """Remove todos os produtos e vendas."""
    qtd_produtos = produtos_collection.count_documents({})
    qtd_vendas = vendas_collection.count_documents({})
    print(f"📦 Produtos: {qtd_produtos}")
    print(f"🧾 Vendas: {qtd_vendas}")

    if qtd_produtos == 0 and qtd_vendas == 0:
        print("✅ Banco já está vazio.")
        return

    confirm = input("⚠️ APAGAR TUDO? (s/N): ")
    if confirm.lower() != 's':
        print("❌ Cancelado.")
        return

    r1 = produtos_collection.delete_many({})
    r2 = vendas_collection.delete_many({})
    print(f"🗑️ {r1.deleted_count} produtos removidos.")
    print(f"🗑️ {r2.deleted_count} vendas removidas.")
    print("✅ Limpeza concluída.")

def corrigir_quantidades():
    """Converte quantidades float para int e zera negativos."""
    produtos = produtos_collection.find({})
    atualizados = 0
    for p in produtos:
        qtd = p.get("quantidade", 0)
        if isinstance(qtd, float) or (isinstance(qtd, int) and qtd < 0):
            nova_qtd = int(qtd) if qtd >= 0 else 0
            produtos_collection.update_one(
                {"_id": p["_id"]},
                {"$set": {"quantidade": nova_qtd}}
            )
            atualizados += 1
    print(f"✅ {atualizados} produtos corrigidos.")

def resetar_estoque(valor=100):
    """Define a quantidade de todos os produtos para um valor padrão."""
    result = produtos_collection.update_many({}, {"$set": {"quantidade": valor}})
    print(f"✅ Estoque de {result.modified_count} produtos resetado para {valor}.")

def rodar_gerador():
    """Executa o script gerar_dados_falsos.py (se existir)."""
    try:
        subprocess.run([sys.executable, "fake_data.py"], check=True)
    except FileNotFoundError:
        print("❌ Arquivo gerar_dados_falsos.py não encontrado.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar gerador: {e}")

def menu():
    print("\n" + "=" * 50)
    print("🛠️  MANUTENÇÃO DO BANCO")
    print("=" * 50)
    print("1. Limpar banco (produtos + vendas)")
    print("2. Corrigir quantidades (float → int)")
    print("3. Resetar estoque para 100")
    print("4. Limpar + Corrigir + Resetar (tudo)")
    print("5. Rodar gerador de dados falsos")
    print("6. Sair")
    print("-" * 50)

if __name__ == "__main__":
    while True:
        menu()
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            limpar_banco()
        elif opcao == "2":
            corrigir_quantidades()
        elif opcao == "3":
            valor = input("Novo valor do estoque (padrão 100): ").strip()
            valor = int(valor) if valor.isdigit() else 100
            resetar_estoque(valor)
        elif opcao == "4":
            print("\n🔄 Executando limpeza, correção e reset...")
            limpar_banco()
            corrigir_quantidades()
            resetar_estoque(100)
            print("\n✅ Tudo pronto para rodar o gerador!")
        elif opcao == "5":
            rodar_gerador()
        elif opcao == "6":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida.")
        input("\nPressione Enter para continuar...")