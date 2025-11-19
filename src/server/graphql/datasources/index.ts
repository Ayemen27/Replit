import { Pool } from 'pg';
import { ProjectsDataSource } from './ProjectsDataSource';
import { CategoriesDataSource } from './CategoriesDataSource';
import { UsersDataSource } from './UsersDataSource';
import { FormsDataSource } from './FormsDataSource';
import { WorkspacesDataSource } from './WorkspacesDataSource';

export { RestDataSource } from './RestDataSource';
export { ProjectsDataSource } from './ProjectsDataSource';
export { CategoriesDataSource } from './CategoriesDataSource';
export { UsersDataSource } from './UsersDataSource';
export { FormsDataSource } from './FormsDataSource';
export { WorkspacesDataSource } from './WorkspacesDataSource';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export interface DataSources {
  projects: ProjectsDataSource;
  categories: CategoriesDataSource;
  users: UsersDataSource;
  forms: FormsDataSource;
  workspaces: WorkspacesDataSource;
}

export function createDataSources(): DataSources {
  return {
    projects: new ProjectsDataSource(),
    categories: new CategoriesDataSource(),
    users: new UsersDataSource(),
    forms: new FormsDataSource(),
    workspaces: new WorkspacesDataSource(pool),
  };
}
