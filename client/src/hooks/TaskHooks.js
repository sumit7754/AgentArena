import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';
import { useEffect, useState } from 'react';

export const useFetchSubmissions = (taskId) => {
  const queryClient = useQueryClient();

  const { data: submissions = [], refetch: fetchSubmissions } = useQuery({
    queryKey: ['submissions', taskId],
    queryFn: async () => {
      if (!taskId) return [];
      const { data } = await axiosInstance.get(`/submissions/task/${taskId}`);
      return data;
    },
    enabled: !!taskId,
  });

  useEffect(() => {
    if (!taskId) return;

    let delay = 1000;
    let maxLimit = 5;
    let attempt = 0;

    const pollSubmissions = async () => {
      if (attempt >= maxLimit) {
        console.log('Max polling attempts reached.');
        return;
      }

      await fetchSubmissions();

      const updatedSubmissions = queryClient.getQueryData(['submissions', taskId]) || [];

      const allCompleted = []
        .concat(updatedSubmissions)
        .every((sub) => sub.status === 'FAILED' || sub.status === 'COMPLETED');

      if (allCompleted) {
        console.log('All submissions completed. Stopping polling.');
        return;
      }

      attempt++;
      delay *= 2;

      setTimeout(pollSubmissions, delay);
    };

    pollSubmissions();
  }, [taskId, queryClient, fetchSubmissions]);

  return submissions;
};

export const useFetchLeaderboard = (taskId) => {
  const { data: leaderboard, refetch: fetchLeaderboard } = useQuery({
    queryKey: ['leaderboard', taskId],
    queryFn: async () => {
      if (!taskId) return [];
      const { data } = await axiosInstance.get(`/submissions/leaderboard/${taskId}`);
      return data;
    },
    enabled: !!taskId,
  });

  return leaderboard;
};

export const useFetchTaskDetail = (taskId) => {
  const { data: taskDetail, refetch: fetchTaskDetail } = useQuery({
    queryKey: ['taskDetail', taskId],
    queryFn: async () => {
      if (!taskId) return null;
      const { data } = await axiosInstance.get(`/tasks/${taskId}`);
      return data;
    },
    enabled: !!taskId, // Fetch only if taskId exists
  });

  return taskDetail;
};
