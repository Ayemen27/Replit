import { SchemaTypeDefinition } from 'sanity'
import project from './project'
import category from './category'
import useCase from './useCase'
import newsPost from './newsPost'
import customerStory from './customerStory'
import productPage from './productPage'
import heroSection from './heroSection'
import page from './page'
import siteSettings from './siteSettings'
import navigationMenu from './navigationMenu'
import footer from './footer'
import objectSchemas from './objects'

const schemas: SchemaTypeDefinition[] = [
  project,
  category,
  useCase,
  newsPost,
  customerStory,
  productPage,
  heroSection,
  page,
  siteSettings,
  navigationMenu,
  footer,
  ...objectSchemas,
]

export default schemas
