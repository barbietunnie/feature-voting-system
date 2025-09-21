import React, { useState, useEffect } from 'react';
import { Users, UserPlus, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { User } from '../types';
import { userApi } from '../services/api';
import { useAuth } from '../hooks/useAuth';

const LoginView: React.FC = () => {
  const { login } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateUser, setShowCreateUser] = useState(false);

  // Create user form state
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      const userData = await userApi.getUsers();
      setUsers(userData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUserSelect = (user: User) => {
    login(user);
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim() || !email.trim()) {
      setError('Username and email are required');
      return;
    }

    try {
      setIsCreating(true);
      setError(null);

      const newUser = await userApi.createUser({
        username: username.trim(),
        email: email.trim(),
      });

      login(newUser);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setIsCreating(false);
    }
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const isFormValid = username.trim().length >= 2 && isValidEmail(email);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-primary rounded-full flex items-center justify-center">
            <Users className="w-8 h-8 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Feature Voting</h1>
            <p className="text-muted-foreground">Select or create your user profile</p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Card className="border-destructive/50 bg-destructive/10">
            <CardContent className="flex items-center gap-2 pt-6">
              <AlertCircle className="w-4 h-4 text-destructive" />
              <p className="text-sm text-destructive">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Existing Users */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Select Existing User</CardTitle>
            <CardDescription>Choose from existing user profiles</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                <span className="ml-2 text-sm text-muted-foreground">Loading users...</span>
              </div>
            ) : users.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">
                No users found. Create the first user!
              </p>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {users.map((user) => (
                  <Button
                    key={user.id}
                    variant="outline"
                    className="w-full justify-start h-auto p-4"
                    onClick={() => handleUserSelect(user)}
                  >
                    <div className="text-left">
                      <div className="font-medium">{user.username}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                    </div>
                  </Button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Create New User Button */}
        <Button
          className="w-full"
          size="lg"
          onClick={() => setShowCreateUser(true)}
        >
          <UserPlus className="w-4 h-4 mr-2" />
          Create New User
        </Button>

        {/* Create User Dialog */}
        <Dialog open={showCreateUser} onOpenChange={setShowCreateUser}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New User</DialogTitle>
              <DialogDescription>
                Enter your details to create a new user profile
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleCreateUser} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium">
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isCreating}
                />
                {username && username.length < 2 && (
                  <p className="text-xs text-destructive">Username must be at least 2 characters</p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isCreating}
                />
                {email && !isValidEmail(email) && (
                  <p className="text-xs text-destructive">Please enter a valid email address</p>
                )}
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateUser(false)}
                  disabled={isCreating}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={!isFormValid || isCreating}
                >
                  {isCreating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2"></div>
                      Creating...
                    </>
                  ) : (
                    'Create User'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default LoginView;