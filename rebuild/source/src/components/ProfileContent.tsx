"use client";

import { useQuery } from '@apollo/client/react';
import { useAuth } from '@/hooks/useAuth';
import { GET_ME, GetMeData } from '@/graphql/queries/user';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

const Avatar = ({ 
  src, 
  alt, 
  initials 
}: { 
  src?: string | null; 
  alt: string; 
  initials: string;
}) => {
  if (src) {
    return (
      <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-white shadow-lg">
        <img src={src} alt={alt} className="w-full h-full object-cover" />
      </div>
    );
  }

  return (
    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center border-4 border-white shadow-lg">
      <span className="text-3xl font-bold text-white">
        {initials}
      </span>
    </div>
  );
};

const Badge = ({ 
  variant = 'default', 
  children 
}: { 
  variant?: 'default' | 'success' | 'inactive'; 
  children: React.ReactNode;
}) => {
  const variants = {
    default: 'bg-blue-100 text-blue-800 border-blue-200',
    success: 'bg-green-100 text-green-800 border-green-200',
    inactive: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${variants[variant]}`}>
      {children}
    </span>
  );
};

const ProfileSkeleton = () => {
  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader className="pb-0">
        <div className="flex flex-col items-center space-y-4 animate-pulse">
          <div className="w-24 h-24 rounded-full bg-gray-200" />
          <div className="h-8 w-48 bg-gray-200 rounded" />
          <div className="h-6 w-32 bg-gray-200 rounded" />
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-4 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
          <div className="h-4 bg-gray-200 rounded w-2/3" />
        </div>
      </CardContent>
    </Card>
  );
};

export default function ProfileContent() {
  const { user: firebaseUser, loading: authLoading } = useAuth();
  const { data, loading, error, refetch } = useQuery<GetMeData>(GET_ME, {
    skip: !firebaseUser,
  });

  if (authLoading || loading) {
    return (
      <div className="min-h-screen p-8">
        <h1 className="text-4xl font-bold mb-8">Profile</h1>
        <ProfileSkeleton />
      </div>
    );
  }

  if (!firebaseUser) {
    return (
      <div className="min-h-screen p-8">
        <h1 className="text-4xl font-bold mb-8">Profile</h1>
        <ErrorMessage 
          message="You must be logged in to view your profile. Please sign in to continue."
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <h1 className="text-4xl font-bold mb-8">Profile</h1>
        <ErrorMessage 
          message={error.message || "Failed to load your profile. Please try again."}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const userData = data?.me;

  if (!userData) {
    return (
      <div className="min-h-screen p-8">
        <h1 className="text-4xl font-bold mb-8">Profile</h1>
        <ErrorMessage 
          message="Profile not found. Please contact support if this issue persists."
        />
      </div>
    );
  }

  const getInitials = () => {
    if (userData.firstName && userData.lastName) {
      return `${userData.firstName[0]}${userData.lastName[0]}`.toUpperCase();
    }
    if (userData.username) {
      return userData.username.slice(0, 2).toUpperCase();
    }
    return userData.email.slice(0, 2).toUpperCase();
  };

  const getFullName = () => {
    if (userData.firstName && userData.lastName) {
      return `${userData.firstName} ${userData.lastName}`;
    }
    return userData.username;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <div className="min-h-screen p-4 sm:p-8">
      <h1 className="text-4xl font-bold mb-8">Profile</h1>
      
      <Card className="max-w-3xl mx-auto">
        <CardHeader className="pb-0">
          <div className="flex flex-col items-center space-y-4">
            <Avatar 
              src={userData.profileImageUrl}
              alt={getFullName()}
              initials={getInitials()}
            />
            <div className="text-center space-y-2">
              <CardTitle className="text-3xl">
                {getFullName()}
              </CardTitle>
              <p className="text-gray-600">@{userData.username}</p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Email Address
              </h3>
              <p className="text-lg text-gray-900 break-all">
                {userData.email}
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Account Status
              </h3>
              <div>
                <Badge variant={userData.isActive ? 'success' : 'inactive'}>
                  {userData.isActive ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>

            {userData.firstName && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                  First Name
                </h3>
                <p className="text-lg text-gray-900">
                  {userData.firstName}
                </p>
              </div>
            )}

            {userData.lastName && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                  Last Name
                </h3>
                <p className="text-lg text-gray-900">
                  {userData.lastName}
                </p>
              </div>
            )}

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Member Since
              </h3>
              <p className="text-lg text-gray-900">
                {formatDate(userData.createdAt)}
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                User ID
              </h3>
              <p className="text-sm text-gray-600 font-mono break-all">
                {userData.id}
              </p>
            </div>
          </div>

          {firebaseUser && (
            <div className="pt-6 border-t border-gray-200">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
                Firebase Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Firebase UID:</span>
                  <p className="font-mono text-xs text-gray-800 break-all mt-1">
                    {firebaseUser.uid}
                  </p>
                </div>
                <div>
                  <span className="text-gray-600">Email Verified:</span>
                  <p className="mt-1">
                    <Badge variant={firebaseUser.emailVerified ? 'success' : 'inactive'}>
                      {firebaseUser.emailVerified ? 'Verified' : 'Not Verified'}
                    </Badge>
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
