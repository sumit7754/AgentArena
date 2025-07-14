import React, { useState, useEffect } from 'react';
import { FiCheck, FiAlertCircle, FiInfo, FiRefreshCw } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';

function PlaygroundHealthCheck() {
  const [healthStatus, setHealthStatus] = useState({
    isLLMServiceReady: false,
    isEvaluationServiceReady: false,
    playgroundStatus: 'unknown',
    isCheckingStatus: true,
    mockMode: true
  });

  useEffect(() => {
    checkPlaygroundHealth();
  }, []);

  const checkPlaygroundHealth = async () => {
    try {
      const response = await axiosInstance.get('/playground/health');
      const data = response.data;
      
      setHealthStatus({
        isLLMServiceReady: data.llm_service || false,
        isEvaluationServiceReady: data.evaluation_service || false,
        playgroundStatus: data.status || 'unknown',
        playgroundVersion: data.playground_version || '1.0.0',
        mockMode: data.mock_mode || false,
        isCheckingStatus: false,
        supportedProviders: data.supported_providers || [],
        supportedEnvironments: data.supported_environments || []
      });
      
      if (data.status === 'healthy') {
        toast.success('Playground is ready!', {
          id: 'playground-health',
          duration: 2000
        });
      } else if (data.status === 'warning') {
        toast.custom(
          (t) => (
            <div className={`${t.visible ? 'animate-enter' : 'animate-leave'} bg-amber-500/90 shadow-md rounded-lg py-2 px-3 text-white`}>
              Playground running with limitations
            </div>
          ),
          { id: 'playground-health' }
        );
      }
    } catch (error) {
      console.error('Error checking playground health:', error);
      setHealthStatus({
        isLLMServiceReady: false,
        isEvaluationServiceReady: false,
        playgroundStatus: 'error',
        isCheckingStatus: false,
        mockMode: true
      });
      toast.error('Failed to check playground status');
    }
  };
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'warning': return 'text-amber-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <div className="text-cyan-200">Playground System Health</div>
        <button 
          onClick={checkPlaygroundHealth}
          className="flex items-center gap-1 text-xs bg-cyan-800/30 hover:bg-cyan-700/40 text-cyan-300 py-1 px-3 rounded-md"
        >
          <FiRefreshCw size={12} />
          Refresh
        </button>
      </div>

      {healthStatus.isCheckingStatus ? (
        <div className="flex items-center gap-2 text-gray-400">
          <div className="animate-pulse h-2 w-2 bg-gray-400 rounded-full"></div>
          Checking system status...
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            {healthStatus.isLLMServiceReady ? (
              <FiCheck className="text-green-400" />
            ) : (
              <FiAlertCircle className="text-amber-400" />
            )}
            <span className={healthStatus.isLLMServiceReady ? 'text-green-300' : 'text-amber-300'}>
              LLM Service: {healthStatus.isLLMServiceReady ? 'Ready' : 'Not Available'}
              {healthStatus.mockMode && healthStatus.isLLMServiceReady && (
                <span className="text-xs bg-gray-700 ml-2 px-2 py-0.5 rounded-full">Mock</span>
              )}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {healthStatus.isEvaluationServiceReady ? (
              <FiCheck className="text-green-400" />
            ) : (
              <FiAlertCircle className="text-amber-400" />
            )}
            <span className={healthStatus.isEvaluationServiceReady ? 'text-green-300' : 'text-amber-300'}>
              Evaluation Service: {healthStatus.isEvaluationServiceReady ? 'Ready' : 'Not Available'}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className={`${getStatusColor(healthStatus.playgroundStatus)} text-sm`}>
              Status: {healthStatus.playgroundStatus.charAt(0).toUpperCase() + healthStatus.playgroundStatus.slice(1)}
              {healthStatus.playgroundVersion && (
                <span className="text-xs bg-gray-700 ml-2 px-2 py-0.5 rounded-full">v{healthStatus.playgroundVersion}</span>
              )}
            </span>
          </div>
          
          {healthStatus.supportedProviders && healthStatus.supportedProviders.length > 0 && (
            <div className="bg-gray-800/70 p-2 rounded-md text-xs mt-2">
              <p className="text-cyan-200 mb-1">Supported LLM Providers:</p>
              <div className="flex flex-wrap gap-1">
                {healthStatus.supportedProviders.map(provider => (
                  <span key={provider} className="bg-gray-700 px-2 py-0.5 rounded-full text-gray-300">
                    {provider}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {healthStatus.playgroundStatus !== 'healthy' && (
            <div className="flex items-center gap-2 bg-gray-800/70 p-2 rounded-md text-xs mt-2">
              <FiInfo className="text-cyan-400" />
              <span className="text-cyan-200">
                {healthStatus.playgroundStatus === 'error' ? 
                  'Playground services are experiencing issues. Results may be limited.' :
                  'Some services are not available. Results may be limited or use mock data.'}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PlaygroundHealthCheck;