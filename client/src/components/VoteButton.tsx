import React from 'react';
import { ThumbsUp, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import type { Feature } from '../types';

interface VoteButtonProps {
  feature: Feature;
  isVoted: boolean;
  isLoading: boolean;
  onVote: () => void;
  onRemoveVote: () => void;
}

const VoteButton: React.FC<VoteButtonProps> = ({
  feature,
  isVoted,
  isLoading,
  onVote,
  onRemoveVote,
}) => {
  const handleClick = () => {
    if (isLoading) return;

    if (isVoted) {
      onRemoveVote();
    } else {
      onVote();
    }
  };

  return (
    <Button
      variant={isVoted ? "default" : "outline"}
      size="sm"
      onClick={handleClick}
      disabled={isLoading}
      className="flex items-center gap-2"
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <ThumbsUp className={`w-4 h-4 ${isVoted ? 'fill-current' : ''}`} />
      )}
      <span className="font-medium">{feature.vote_count}</span>
      <span className="text-xs">
        {feature.vote_count === 1 ? 'vote' : 'votes'}
      </span>
    </Button>
  );
};

export default VoteButton;