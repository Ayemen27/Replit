import { userRepository, User } from '@/lib/db/repositories';
import bcrypt from 'bcrypt';

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

export class UsersDataSource {
  private transformUser(user: User) {
    return {
      id: user.id,
      username: user.username || user.name || 'user',
      name: user.name,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      avatarUrl: user.avatar_url || user.image,
      profileImageUrl: user.avatar_url || user.image,
      isActive: user.is_active,
      createdAt: user.created_at.toISOString(),
      updatedAt: user.updated_at.toISOString(),
    };
  }

  async me(userId: string) {
    const user = await userRepository.findById(userId);
    
    if (!user) {
      throw new Error('User not found');
    }
    
    return this.transformUser(user);
  }

  async signup(input: SignupInput) {
    const existingUser = await userRepository.findByEmail(input.email);
    if (existingUser) {
      throw new Error('Email already exists');
    }

    if (input.username) {
      const existingUsername = await userRepository.findByUsername(input.username);
      if (existingUsername) {
        throw new Error('Username already exists');
      }
    }

    const hashedPassword = await bcrypt.hash(input.password, 10);

    const user = await userRepository.createUser({
      email: input.email,
      name: input.username || input.email.split('@')[0],
      password: hashedPassword,
    });

    if (input.firstName || input.lastName || input.username) {
      await userRepository.updateUser(user.id, {
        first_name: input.firstName,
        last_name: input.lastName,
        username: input.username,
      } as Partial<User>);
    }

    const updatedUser = await userRepository.findById(user.id);
    
    return {
      user: this.transformUser(updatedUser!),
      accessToken: 'temporary_token',
      refreshToken: 'temporary_refresh_token',
    };
  }

  async login(input: LoginInput) {
    const user = await userRepository.findByEmailOrUsername(input.emailOrUsername);
    
    if (!user) {
      throw new Error('Invalid credentials');
    }

    if (!user.password) {
      throw new Error('Invalid credentials');
    }

    const isValidPassword = await bcrypt.compare(input.password, user.password);
    
    if (!isValidPassword) {
      throw new Error('Invalid credentials');
    }

    return {
      user: this.transformUser(user),
      accessToken: 'temporary_token',
      refreshToken: 'temporary_refresh_token',
    };
  }
}
