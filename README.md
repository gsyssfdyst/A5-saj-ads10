# A5-saj-ads10

Projeto: Sistema distribuído (asyncio + gRPC + TCP sockets + multicast UDP + Bully + Lamport + Snapshot + Auth por JWT)

Instruções rápidas para executar o projeto (Ubuntu 24.04 / Python 3.11+)

1) Pré-requisitos do sistema (se necessário):
   sudo apt update
   sudo apt install -y python3-venv python3-dev build-essential

2) Criar e ativar venv:
   python3 -m venv venv
   source venv/bin/activate

3) Instalar dependências:
   pip install -r requirements.txt

4) (Opcional) Compilar protos para app/proto:
   python scripts/compile_protos.py
   # ou use grpc_tools.protoc manualmente apontando proto/ -> app/proto

5) Iniciar nós (abra um terminal por nó):
   python scripts/run_node.py --id 1 --port 9001 --peers 127.0.0.1:9002:2,127.0.0.1:9003:3
   python scripts/run_node.py --id 2 --port 9002 --peers 127.0.0.1:9001:1,127.0.0.1:9003:3
   python scripts/run_node.py --id 3 --port 9003 --peers 127.0.0.1:9001:1,127.0.0.1:9002:2

   - Cada nó também inicia um servidor gRPC no porto (node_port + 1000),
     ex.: node 9001 -> gRPC 10001.

6) Emitir token JWT (pelo líder ou para testes):
   python scripts/run_node.py --id 1 --port 9001 --issue-token
   # imprime um JWT assinado com o secret configurado (NODE_SECRET / --secret)

7) Testar gRPC (exemplo com grpcurl):
   grpcurl -plaintext -H "authorization: Bearer <JWT>" localhost:10001 monitor.Monitor/GetStatus

   Ou usar um cliente Python gRPC incluindo metadata ("authorization": "Bearer <JWT>").

8) Ouvir multicast (cliente):
   python scripts/client_multicast.py --group 224.0.0.1 --port 5007

9) Rodar testes:
   pytest -q

Dicas rápidas:
- Se um nó não responder, os peers detectam falha por heartbeat e disparam eleição (Bully).
- O snapshot é iniciado pelo líder com node.initiate_snapshot() (exponha via RPC se desejar).
- Logs e erros aparecem no terminal do nó; para múltiplos nós use tmux/screen ou background (&).