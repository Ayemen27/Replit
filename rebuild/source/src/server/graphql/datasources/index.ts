import { ProjectsDataSource } from './ProjectsDataSource';
import { CategoriesDataSource } from './CategoriesDataSource';
import { UsersDataSource } from './UsersDataSource';
import { FormsDataSource } from './FormsDataSource';

export { RestDataSource } from './RestDataSource';
export { ProjectsDataSource } from './ProjectsDataSource';
export { CategoriesDataSource } from './CategoriesDataSource';
export { UsersDataSource } from './UsersDataSource';
export { FormsDataSource } from './FormsDataSource';

export interface DataSources {
  projects: ProjectsDataSource;
  categories: CategoriesDataSource;
  users: UsersDataSource;
  forms: FormsDataSource;
}

export function createDataSources(): DataSources {
  return {
    projects: new ProjectsDataSource(),
    categories: new CategoriesDataSource(),
    users: new UsersDataSource(),
    forms: new FormsDataSource(),
  };
}
