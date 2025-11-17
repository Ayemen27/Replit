const commonSchema = `
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
  page: Int!
  perPage: Int!
  totalPages: Int!
}

type Query
type Mutation
`;

const userSchema = `
type User {
  id: ID!
  username: String!
  email: String!
  name: String
  firstName: String
  lastName: String
  avatarUrl: String
  profileImageUrl: String
  isActive: Boolean!
  createdAt: String!
}

type AuthPayload {
  accessToken: String!
  refreshToken: String!
  user: User!
}

input SignupInput {
  username: String!
  email: String!
  password: String!
  firstName: String
  lastName: String
}

input LoginInput {
  emailOrUsername: String!
  password: String!
}

extend type Query {
  me: User
}

extend type Mutation {
  signup(input: SignupInput!): AuthPayload!
  login(input: LoginInput!): AuthPayload!
}
`;

const categorySchema = `
type Category {
  id: ID!
  name: String!
  slug: String!
  description: String
  icon: String
}

extend type Query {
  categories: [Category!]!
  category(slug: String!): Category
}
`;

const projectSchema = `
type Project {
  id: ID!
  title: String!
  slug: String!
  description: String
  imageUrl: String
  demoUrl: String
  replUrl: String
  author: User
  category: Category
  isFeatured: Boolean!
  viewsCount: Int!
  likesCount: Int!
  createdAt: String!
}

type ProjectConnection {
  projects: [Project!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

input CreateProjectInput {
  title: String!
  slug: String!
  description: String!
  imageUrl: String
  demoUrl: String
  replUrl: String
  categoryId: ID
}

extend type Query {
  projects(
    featured: Boolean
    category: String
    page: Int = 1
    perPage: Int = 12
  ): ProjectConnection!
  
  project(slug: String!): Project
  
  featuredProjects(perPage: Int = 6): [Project!]!
}

extend type Mutation {
  createProject(input: CreateProjectInput!): Project!
}
`;

const formSchema = `
scalar JSON

type FormSubmission {
  id: ID!
  formType: String!
  name: String
  email: String!
  company: String
  message: String
  phone: String
  status: String
  extraData: JSON
  createdAt: String!
}

input FormSubmissionInput {
  formType: String!
  name: String!
  email: String!
  company: String
  message: String
  phone: String
  extraData: JSON
}

extend type Mutation {
  submitForm(input: FormSubmissionInput!): FormSubmission!
}
`;

export const typeDefs = `
${commonSchema}
${userSchema}
${categorySchema}
${projectSchema}
${formSchema}
`;

export default typeDefs;
