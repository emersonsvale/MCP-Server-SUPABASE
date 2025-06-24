# Servidor MCP para Supabase

Servidor MCP (Model Context Protocol) para integração dinâmica com Supabase.

## Características

- ✅ Configuração dinâmica por projeto
- ✅ Suporte a múltiplos projetos Supabase
- ✅ Operações de banco de dados
- ✅ Autenticação de usuários
- ✅ Armazenamento de arquivos
- ✅ Funcionalidades em tempo real
- ✅ Deploy automático no Coolify

## Configuração

### Variáveis de Ambiente

```env
# Configurações padrão do Supabase (fallback)
DEFAULT_SUPABASE_URL=https://your-default-project.supabase.co
DEFAULT_SUPABASE_ANON_KEY=your-default-anon-key-here
DEFAULT_SUPABASE_SERVICE_KEY=your-default-service-key-here

# Configurações do servidor
DEBUG=false
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
```

### Uso Dinâmico

O servidor suporta configuração dinâmica via headers:

```javascript
// Headers suportados
x-supabase-project: seu-projeto-abc123
x-supabase-token: sua-chave-anon-aqui
```

## Deploy no Coolify

1. Clone este repositório
2. Configure as variáveis de ambiente no Coolify
3. Deploy usando Docker Compose

## Ferramentas Disponíveis

### Banco de Dados
- `database_query` - Query SQL personalizada
- `database_select` - Selecionar registros
- `database_insert` - Inserir registro
- `database_update` - Atualizar registro
- `database_delete` - Deletar registro
- `database_list_tables` - Listar tabelas
- `database_get_project_info` - Informações do projeto

### Autenticação
- `auth_sign_up` - Registrar usuário
- `auth_sign_in` - Login
- `auth_sign_out` - Logout
- `auth_get_user` - Obter usuário atual
- `auth_reset_password` - Reset de senha
- `auth_update_user` - Atualizar usuário

### Armazenamento
- `storage_upload` - Upload de arquivo
- `storage_download` - Download de arquivo
- `storage_list_files` - Listar arquivos
- `storage_delete_file` - Deletar arquivo
- `storage_get_url` - Obter URL pública
- `storage_list_buckets` - Listar buckets

### Tempo Real
- `realtime_subscribe` - Inscrever em mudanças
- `realtime_unsubscribe` - Cancelar inscrição
- `realtime_list_subscriptions` - Listar inscrições
- `realtime_broadcast` - Enviar mensagem
- `realtime_subscribe_channel` - Inscrever em canal

## Integração com n8n

```javascript
// Exemplo de uso no n8n
const response = await $http.post('http://seu-mcp-server:8000/mcp/call_tool', {
  name: 'database_select',
  arguments: {
    table: 'users',
    limit: 5
  }
}, {
  headers: {
    'x-supabase-project': 'seu-projeto-abc123',
    'x-supabase-token': 'sua-chave-anon-aqui',
    'Content-Type': 'application/json'
  }
});
```

## Licença

MIT 