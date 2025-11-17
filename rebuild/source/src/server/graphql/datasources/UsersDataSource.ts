import { RestDataSource } from './RestDataSource';

interface RestUser {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile_image_url?: string;
  bio?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

interface SignupInput {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

interface LoginInput {
  emailOrUsername: string;
  password: string;
}

interface AuthResponse {
  message: string;
  user: RestUser;
  access_token: string;
  refresh_token: string;
}

interface MeResponse {
  user: RestUser;
}

export class UsersDataSource extends RestDataSource {
  private transformUser(user: RestUser) {
    return {
      id: user.id,
      username: user.username,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      profileImageUrl: user.profile_image_url,
      bio: user.bio,
      isActive: user.is_active,
      isAdmin: user.is_admin,
      createdAt: user.created_at,
      updatedAt: user.updated_at,
    };
  }

  async me(token: string) {
    const response = await this.get<MeResponse>('/auth/me', token);
    return this.transformUser(response.user);
  }

  async signup(input: SignupInput) {
    const body = {
      email: input.email,
      username: input.username,
      password: input.password,
      first_name: input.firstName,
      last_name: input.lastName,
    };

    const response = await this.post<AuthResponse>('/auth/signup', body);

    return {
      user: this.transformUser(response.user),
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
    };
  }

  async login(input: LoginInput) {
    const body = {
      email_or_username: input.emailOrUsername,
      password: input.password,
    };

    const response = await this.post<AuthResponse>('/auth/login', body);

    return {
      user: this.transformUser(response.user),
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
    };
  }
}
