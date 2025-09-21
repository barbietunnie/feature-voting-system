import React, { useState } from 'react';
import { Plus, User, LogOut, Lightbulb, Flame, Star, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import VoteButton from './VoteButton';
import AddFeatureModal from './AddFeatureModal';
import { useAuth } from '../hooks/useAuth';
import { useFeatures } from '../hooks/useFeatures';
import { Feature } from '../types';

const FeatureList: React.FC = () => {
  const { user, logout } = useAuth();
  const {
    features,
    isLoading,
    isLoadingMore,
    error,
    hasMore,
    votedFeatures,
    votingInProgress,
    loadMoreFeatures,
    refreshFeatures,
    createFeature,
    voteForFeature,
    removeVote,
    clearError,
  } = useFeatures();

  const [showAddFeature, setShowAddFeature] = useState(false);

  const handleRefresh = async () => {
    await refreshFeatures();
  };

  const getFeatureIcon = (voteCount: number) => {
    if (voteCount > 10) {
      return <Flame className="w-4 h-4 text-orange-500" />;
    } else if (voteCount > 5) {
      return <Star className="w-4 h-4 text-yellow-500" />;
    }
    return null;
  };

  if (isLoading && features.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          <span>Loading features...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Features</h1>

          <div className="flex items-center gap-2">
            {/* User Menu */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="w-4 h-4" />
              <span>{user?.username}</span>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
            >
              <LogOut className="w-4 h-4" />
            </Button>

            {/* Add Feature Button */}
            <Button onClick={() => setShowAddFeature(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Feature
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {/* Error Display */}
        {error && (
          <Card className="mb-6 border-destructive/50 bg-destructive/10">
            <CardContent className="flex items-center justify-between pt-6">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-destructive" />
                <p className="text-sm text-destructive">{error}</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearError}
              >
                Dismiss
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Features List */}
        {features.length === 0 && !isLoading ? (
          <EmptyState onAddFeature={() => setShowAddFeature(true)} />
        ) : (
          <div className="space-y-4">
            {features.map((feature) => (
              <FeatureCard
                key={feature.id}
                feature={feature}
                isVoted={votedFeatures.has(feature.id)}
                isVoting={votingInProgress.has(feature.id)}
                onVote={() => voteForFeature(feature)}
                onRemoveVote={() => removeVote(feature)}
              />
            ))}

            {/* Load More Button */}
            {hasMore && (
              <div className="flex justify-center pt-6">
                <Button
                  variant="outline"
                  onClick={loadMoreFeatures}
                  disabled={isLoadingMore}
                >
                  {isLoadingMore ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
                      Loading more...
                    </>
                  ) : (
                    'Load More'
                  )}
                </Button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Add Feature Modal */}
      <AddFeatureModal
        open={showAddFeature}
        onOpenChange={setShowAddFeature}
        onSubmit={createFeature}
      />
    </div>
  );
};

interface FeatureCardProps {
  feature: Feature;
  isVoted: boolean;
  isVoting: boolean;
  onVote: () => void;
  onRemoveVote: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  feature,
  isVoted,
  isVoting,
  onVote,
  onRemoveVote,
}) => {
  const getFeatureIcon = (voteCount: number) => {
    if (voteCount > 10) {
      return <Flame className="w-4 h-4 text-orange-500" />;
    } else if (voteCount > 5) {
      return <Star className="w-4 h-4 text-yellow-500" />;
    }
    return null;
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="space-y-1 flex-1">
            <CardTitle className="text-lg">{feature.title}</CardTitle>
            <CardDescription>{feature.description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className={feature.vote_count > 0 ? 'text-primary font-medium' : ''}>
              {feature.vote_count} {feature.vote_count === 1 ? 'vote' : 'votes'}
            </span>
            {getFeatureIcon(feature.vote_count)}
          </div>

          <VoteButton
            feature={feature}
            isVoted={isVoted}
            isLoading={isVoting}
            onVote={onVote}
            onRemoveVote={onRemoveVote}
          />
        </div>
      </CardContent>
    </Card>
  );
};

const EmptyState: React.FC<{ onAddFeature: () => void }> = ({ onAddFeature }) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
      <Lightbulb className="w-8 h-8 text-muted-foreground" />
    </div>
    <h3 className="text-lg font-medium mb-2">No features yet</h3>
    <p className="text-muted-foreground mb-4">Be the first to suggest a feature!</p>
    <Button onClick={onAddFeature}>
      <Plus className="w-4 h-4 mr-2" />
      Add Feature
    </Button>
  </div>
);

export default FeatureList;