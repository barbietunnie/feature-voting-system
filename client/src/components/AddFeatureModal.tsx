import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import type { CreateFeatureRequest } from '../types';

interface AddFeatureModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (featureData: CreateFeatureRequest) => Promise<boolean>;
}

const AddFeatureModal: React.FC<AddFeatureModalProps> = ({
  open,
  onOpenChange,
  onSubmit,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isFormValid) {
      return;
    }

    setIsSubmitting(true);

    try {
      const success = await onSubmit({
        title: title.trim(),
        description: description.trim(),
      });

      if (success) {
        // Reset form and close modal
        setTitle('');
        setDescription('');
        onOpenChange(false);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setTitle('');
      setDescription('');
      onOpenChange(false);
    }
  };

  const isFormValid =
    title.trim().length >= 3 &&
    title.trim().length <= 100 &&
    description.trim().length >= 10 &&
    description.trim().length <= 1000;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add New Feature</DialogTitle>
          <DialogDescription>
            Suggest a new feature for the application
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="title" className="text-sm font-medium">
              Title
            </label>
            <Input
              id="title"
              type="text"
              placeholder="Feature title..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isSubmitting}
              maxLength={100}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>
                {title.length < 3 && title.length > 0 && (
                  <span className="text-destructive">At least 3 characters required</span>
                )}
                {title.length >= 3 && (
                  <span className="text-green-600">✓ Title looks good</span>
                )}
              </span>
              <span>{title.length}/100</span>
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="description" className="text-sm font-medium">
              Description
            </label>
            <Textarea
              id="description"
              placeholder="Describe the feature in detail..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isSubmitting}
              rows={4}
              maxLength={1000}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>
                {description.length < 10 && description.length > 0 && (
                  <span className="text-destructive">At least 10 characters required</span>
                )}
                {description.length >= 10 && (
                  <span className="text-green-600">✓ Description looks good</span>
                )}
              </span>
              <span>{description.length}/1000</span>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!isFormValid || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2"></div>
                  Creating...
                </>
              ) : (
                'Create Feature'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddFeatureModal;