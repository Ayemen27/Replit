import { gql } from '@apollo/client';

export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  profileImageUrl?: string;
  isActive: boolean;
  createdAt: string;
}

export interface GetMeData {
  me: User | null;
}

export const GET_ME = gql`
  query GetMe {
    me {
      id
      username
      email
      firstName
      lastName
      profileImageUrl
      isActive
      createdAt
    }
  }
`;
