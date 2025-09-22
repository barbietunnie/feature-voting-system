import { useState, useEffect } from 'react';
import type { Feature, CreateFeatureRequest, PaginatedResponse } from '../types';
import { featureApi } from '../services/api';

export const useFeatures = () => {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [votedFeatures, setVotedFeatures] = useState<Set<number>>(new Set());
  const [votingInProgress, setVotingInProgress] = useState<Set<number>>(new Set());

  const pageSize = 20;

  const loadFeatures = async (page = 1, reset = true) => {
    if (reset) {
      setIsLoading(true);
      setError(null);
    } else {
      setIsLoadingMore(true);
    }

    try {
      const response: PaginatedResponse<Feature> = await featureApi.getFeatures(page, pageSize);

      if (reset) {
        setFeatures(response.items);
      } else {
        setFeatures(prev => [...prev, ...response.items]);
      }

      setCurrentPage(response.page);
      setHasMore(response.has_next);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load features');
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  const loadMoreFeatures = async () => {
    if (hasMore && !isLoadingMore) {
      await loadFeatures(currentPage + 1, false);
    }
  };

  const refreshFeatures = async () => {
    await loadFeatures(1, true);
  };

  const createFeature = async (featureData: CreateFeatureRequest): Promise<boolean> => {
    try {
      const newFeature = await featureApi.createFeature(featureData);
      setFeatures(prev => [newFeature, ...prev]);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create feature');
      return false;
    }
  };

  const voteForFeature = async (feature: Feature): Promise<boolean> => {
    if (votingInProgress.has(feature.id)) return false;

    setVotingInProgress(prev => new Set([...prev, feature.id]));

    try {
      const response = await featureApi.voteForFeature(feature.id);

      // Update the feature's vote count locally
      setFeatures(prev => prev.map(f =>
        f.id === feature.id
          ? { ...f, vote_count: response.vote_count }
          : f
      ));

      // Mark as voted
      setVotedFeatures(prev => new Set([...prev, feature.id]));

      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to vote for feature');
      return false;
    } finally {
      setVotingInProgress(prev => {
        const newSet = new Set(prev);
        newSet.delete(feature.id);
        return newSet;
      });
    }
  };

  const removeVote = async (feature: Feature): Promise<boolean> => {
    if (votingInProgress.has(feature.id)) return false;

    setVotingInProgress(prev => new Set([...prev, feature.id]));

    try {
      const response = await featureApi.removeVote(feature.id);

      // Update the feature's vote count locally
      setFeatures(prev => prev.map(f =>
        f.id === feature.id
          ? { ...f, vote_count: response.vote_count }
          : f
      ));

      // Remove from voted
      setVotedFeatures(prev => {
        const newSet = new Set(prev);
        newSet.delete(feature.id);
        return newSet;
      });

      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove vote');
      return false;
    } finally {
      setVotingInProgress(prev => {
        const newSet = new Set(prev);
        newSet.delete(feature.id);
        return newSet;
      });
    }
  };

  const clearError = () => {
    setError(null);
  };

  // Load features on mount
  useEffect(() => {
    loadFeatures();
  }, []);

  return {
    features,
    isLoading,
    isLoadingMore,
    error,
    hasMore,
    votedFeatures,
    votingInProgress,
    loadFeatures,
    loadMoreFeatures,
    refreshFeatures,
    createFeature,
    voteForFeature,
    removeVote,
    clearError,
  };
};