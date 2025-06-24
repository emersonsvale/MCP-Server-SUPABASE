// Exemplo de uso no n8n com configuração dinâmica

// 1. Configuração via headers (recomendado)
const mcpServerUrl = 'http://seu-dominio:8000';
const projectCode = 'seu-projeto-abc123';
const accessToken = 'sua-chave-anon-aqui';

// Fazer chamada com headers
const response = await $http.post(`${mcpServerUrl}/mcp/call_tool`, {
  name: 'database_select',
  arguments: {
    table: 'users',
    limit: 10
  }
}, {
  headers: {
    'x-supabase-project': projectCode,
    'x-supabase-token': accessToken,
    'Content-Type': 'application/json'
  }
});

// 2. Configuração via parâmetros (alternativo)
const response2 = await $http.post(`${mcpServerUrl}/mcp/call_tool`, {
  name: 'database_select',
  arguments: {
    table: 'users',
    limit: 10,
    project_code: projectCode,
    access_token: accessToken
  }
}, {
  headers: {
    'Content-Type': 'application/json'
  }
});

// 3. Verificar informações do projeto
const projectInfo = await $http.post(`${mcpServerUrl}/mcp/call_tool`, {
  name: 'database_get_project_info',
  arguments: {}
}, {
  headers: {
    'x-supabase-project': projectCode,
    'x-supabase-token': accessToken,
    'Content-Type': 'application/json'
  }
});

console.log('Projeto atual:', projectInfo.data); 