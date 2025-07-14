import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { AiOutlineArrowLeft, AiOutlinePlus, AiOutlineDelete, AiOutlineEdit } from 'react-icons/ai';
import { Link, useNavigate } from 'react-router-dom';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';

function CreateAgent() {
  const navigate = useNavigate();

  const [agentInput, setAgentInput] = useState({
    name: '',
    description: '',
    configType: 'real', // real or mock
    agentType: 'gpt-4',
    configurationJson: {
      llm_provider: 'openai',
      llm_model: 'gpt-4',
      temperature: 0.7,
      max_output_tokens: 2000,
      system_prompt: 'You are a helpful assistant.'
    }
  });

  const [llmApiKey, setLlmApiKey] = useState('');
  const [availableModels, setAvailableModels] = useState({
    openai: ['gpt-4', 'gpt-4o', 'gpt-3.5-turbo'],
    anthropic: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    google: ['gemini-1.5-pro', 'gemini-1.5-flash'],
    azure_openai: ['gpt-4', 'gpt-3.5-turbo'],
    ollama: ['llama3', 'mistral', 'phi3'],
    huggingface_inference: ['meta-llama/Llama-2-70b-chat-hf', 'mistralai/Mistral-7B-Instruct-v0.1']
  });
  
  const [advancedMode, setAdvancedMode] = useState(false);
  const [jsonEditorValue, setJsonEditorValue] = useState('');
  const [jsonError, setJsonError] = useState(null);
  const [supportedProviders, setSupportedProviders] = useState([]);
  const [mockMode, setMockMode] = useState(true);

  useEffect(() => {
    // Update JSON editor value when configuration changes
    const jsonString = JSON.stringify(agentInput.configurationJson, null, 2);
    setJsonEditorValue(jsonString);
    
    // Check playground health to get supported providers
    checkPlaygroundHealth();
  }, [agentInput.configurationJson]);

  const checkPlaygroundHealth = async () => {
    try {
      const response = await axiosInstance.get('/playground/health');
      const data = response.data;
      
      setSupportedProviders(data.supported_providers || []);
      setMockMode(data.mock_mode || true);
    } catch (error) {
      console.error('Error checking playground health:', error);
      setSupportedProviders([]);
      setMockMode(true);
    }
  };

  function handleInputChange(e) {
    const { name, value } = e.target;
    
    if (name === 'configType' && value === 'mock') {
      // If switching to mock config, update agentType
      setAgentInput({
        ...agentInput,
        [name]: value,
        agentType: 'mock'
      });
    } else {
      setAgentInput({ ...agentInput, [name]: value });
    }
  }

  function handleConfigChange(field, value) {
    setAgentInput({
      ...agentInput,
      configurationJson: {
        ...agentInput.configurationJson,
        [field]: value
      }
    });
  }
  
  function handleLlmApiKeyChange(e) {
    setLlmApiKey(e.target.value);
  }
  
  function handleProviderChange(e) {
    const provider = e.target.value;
    const defaultModel = availableModels[provider]?.[0] || '';
    
    setAgentInput({
      ...agentInput,
      configurationJson: {
        ...agentInput.configurationJson,
        llm_provider: provider,
        llm_model: defaultModel
      }
    });
  }
  
  function handleJsonEditorChange(e) {
    const jsonValue = e.target.value;
    setJsonEditorValue(jsonValue);
    
    try {
      const parsedJson = JSON.parse(jsonValue);
      setAgentInput({
        ...agentInput,
        configurationJson: parsedJson
      });
      setJsonError(null);
    } catch (error) {
      setJsonError('Invalid JSON: ' + error.message);
    }
  }

  async function onFormSubmit(e) {
    e.preventDefault();

    if (!agentInput.name) {
      toast.error('Agent name is required');
      return;
    }

    try {
      // Use the regular /agents endpoint which accepts the simplified schema
      const agentData = {
        name: agentInput.name,
        description: agentInput.description,
        agentType: agentInput.agentType,
        configurationJson: agentInput.configurationJson
      };

      const response = await axiosInstance.post('/agents', agentData);

      toast.success('Agent created successfully!');
      
      // Store API key in session storage for later use during submission
      if (llmApiKey && agentInput.configType === 'real') {
        // Store with agent ID as part of the key
        sessionStorage.setItem(`llm_api_key_${response.data.id}`, llmApiKey);
      }
      
      navigate('/agents');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create agent');
    }
  }

  return (
    <HomeLayout>
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <form
          onSubmit={onFormSubmit}
          className="bg-gray-800 p-8 rounded-lg shadow-xl w-full max-w-3xl border border-cyan-500/20"
        >
          <div className="mb-6">
            <Link to="/agents" className="text-cyan-400 hover:text-cyan-300 transition-colors">
              <AiOutlineArrowLeft className="text-2xl" />
            </Link>
            <h1 className="text-center text-3xl font-bold mt-4 bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
              Create New Agent
            </h1>
            <p className="text-center text-cyan-200 mt-2">Configure your AI agent for benchmark testing</p>
          </div>

          <div className="space-y-6">
            <div className="flex flex-col gap-2">
              <label className="text-lg font-semibold text-white">Agent Name</label>
              <input
                type="text"
                name="name"
                className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
                placeholder="Enter agent name"
                value={agentInput.name}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-lg font-semibold text-white">Description</label>
              <textarea
                name="description"
                className="bg-gray-700 border border-gray-600 p-3 rounded-lg h-24 resize-none text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
                placeholder="Describe your agent's capabilities and purpose"
                value={agentInput.description}
                onChange={handleInputChange}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-lg font-semibold text-white">Configuration Type</label>
                <select
                  name="configType"
                  className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white focus:border-cyan-500 focus:outline-none transition-colors"
                  value={agentInput.configType}
                  onChange={handleInputChange}
                  required
                >
                  <option value="real">🔌 Real LLM Connection</option>
                  <option value="mock">🧪 Mock (Testing)</option>
                </select>
              </div>

              {agentInput.configType === 'real' && (
                <div className="flex flex-col gap-2">
                  <label className="text-lg font-semibold text-white">LLM API Key</label>
                  <input
                    type="password"
                    className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
                    placeholder="Your API key (stored securely in your browser)"
                    value={llmApiKey}
                    onChange={handleLlmApiKeyChange}
                  />
                  <p className="text-xs text-amber-400">Your API key is never sent to our servers. It's stored temporarily in your browser.</p>
                </div>
              )}
              
              {(mockMode || agentInput.configType === 'mock') && (
                <div className="flex flex-col gap-2">
                  <label className="text-lg font-semibold text-white">Agent Type</label>
                  <select
                    name="agentType"
                    className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white focus:border-cyan-500 focus:outline-none transition-colors"
                    value={agentInput.agentType}
                    onChange={handleInputChange}
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5</option>
                    <option value="claude-3-opus">Claude 3 Opus</option>
                    <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                    <option value="mock">Mock Agent</option>
                  </select>
                </div>
              )}
            </div>

            <div className="bg-gray-750 rounded-lg p-4 border border-gray-600">
              <h3 className="text-lg font-semibold text-white mb-4">LLM Configuration</h3>
              
              {agentInput.configType === 'real' && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-cyan-200">LLM Provider</label>
                      <select
                        className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white focus:border-cyan-500 focus:outline-none transition-colors"
                        value={agentInput.configurationJson.llm_provider}
                        onChange={handleProviderChange}
                      >
                        {supportedProviders.length > 0 ? (
                          supportedProviders.map(provider => (
                            <option key={provider} value={provider}>
                              {provider.charAt(0).toUpperCase() + provider.slice(1)}
                            </option>
                          ))
                        ) : (
                          <>
                            <option value="openai">OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                            <option value="google">Google AI</option>
                            <option value="azure_openai">Azure OpenAI</option>
                            <option value="ollama">Ollama (Local)</option>
                            <option value="huggingface_inference">HuggingFace Inference</option>
                          </>
                        )}
                      </select>
                    </div>
                    
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-cyan-200">Model</label>
                      <select
                        className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white focus:border-cyan-500 focus:outline-none transition-colors"
                        value={agentInput.configurationJson.llm_model}
                        onChange={(e) => handleConfigChange('llm_model', e.target.value)}
                      >
                        {availableModels[agentInput.configurationJson.llm_provider]?.map((model) => (
                          <option key={model} value={model}>
                            {model}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-cyan-200">Temperature</label>
                      <div className="flex items-center gap-3">
                        <input
                          type="range"
                          min="0"
                          max="2"
                          step="0.1"
                          className="flex-1"
                          value={agentInput.configurationJson.temperature}
                          onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                        />
                        <span className="w-12 text-right text-white">{agentInput.configurationJson.temperature}</span>
                      </div>
                    </div>
                    
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-cyan-200">Max Output Tokens</label>
                      <input
                        type="number"
                        className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white focus:border-cyan-500 focus:outline-none transition-colors"
                        value={agentInput.configurationJson.max_output_tokens}
                        onChange={(e) => handleConfigChange('max_output_tokens', parseInt(e.target.value))}
                        min="1"
                        max="8000"
                      />
                    </div>
                  </div>
                </>
              )}
              
              <div className="flex flex-col gap-2 mb-4">
                <label className="text-sm font-medium text-cyan-200">System Prompt</label>
                <textarea
                  className="bg-gray-700 border border-gray-600 p-3 rounded-lg h-24 resize-none text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
                  placeholder="Initial instructions for the LLM"
                  value={agentInput.configurationJson.system_prompt}
                  onChange={(e) => handleConfigChange('system_prompt', e.target.value)}
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 text-sm"
                  onClick={() => setAdvancedMode(!advancedMode)}
                >
                  <AiOutlineEdit size={16} />
                  {advancedMode ? 'Hide' : 'Show'} Advanced Editor
                </button>
              </div>
              
              {advancedMode && (
                <div className="mt-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-cyan-200">Configuration JSON</label>
                    <textarea
                      className={`bg-gray-700 border ${jsonError ? 'border-red-500' : 'border-gray-600'} p-3 rounded-lg h-64 font-mono text-sm text-white focus:border-cyan-500 focus:outline-none transition-colors`}
                      value={jsonEditorValue}
                      onChange={handleJsonEditorChange}
                    />
                    {jsonError && (
                      <p className="text-red-400 text-xs mt-1">{jsonError}</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="bg-blue-900/20 border border-blue-400/30 rounded-lg p-4">
              <h3 className="text-blue-300 font-semibold mb-2">💡 Important Information</h3>
              <ul className="text-sm text-blue-200 space-y-1">
                <li>• Your API key is <strong>never</strong> sent to our servers</li>
                <li>• Keys are stored temporarily in your browser session</li>
                <li>• You'll need to provide your key each time you run a benchmark</li>
                <li>• Benchmark tasks may require specific LLM capabilities</li>
              </ul>
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold py-3 rounded-lg hover:from-cyan-600 hover:to-blue-700 transform hover:scale-105 transition-all duration-200"
              >
                Create Agent
              </button>
              <Link to="/agents" className="flex-1">
                <button
                  type="button"
                  className="w-full border-2 border-gray-600 text-gray-300 font-semibold py-3 rounded-lg hover:border-gray-500 hover:text-white transition-all duration-200"
                >
                  Cancel
                </button>
              </Link>
            </div>
          </div>
        </form>
      </div>
    </HomeLayout>
  );
}

export default CreateAgent;
