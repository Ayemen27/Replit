import richText from './richText'
import customImage from './customImage'
import link from './link'
import button from './button'
import codeSnippet from './codeSnippet'
import person from './person'
import metric from './metric'
import formField from './formField'
import contentReference from './contentReference'
import { sectionSchemas } from './sections'

export const objectSchemas = [
  richText,
  customImage,
  link,
  button,
  codeSnippet,
  person,
  metric,
  formField,
  contentReference,
  ...sectionSchemas,
]

export default objectSchemas
