import { defineType } from 'sanity'

export default defineType({
  name: 'link',
  title: 'Link',
  type: 'object',
  fields: [
    {
      name: 'linkType',
      title: 'Link Type',
      type: 'string',
      options: {
        list: [
          { title: 'Internal', value: 'internal' },
          { title: 'External', value: 'external' },
        ],
        layout: 'radio',
      },
      initialValue: 'internal',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'internalLink',
      title: 'Internal Link',
      type: 'reference',
      to: [
        { type: 'page' },
        { type: 'productPage' },
        { type: 'newsPost' },
        { type: 'customerStory' },
        { type: 'useCase' },
      ],
      hidden: ({ parent }) => parent?.linkType !== 'internal',
    },
    {
      name: 'externalUrl',
      title: 'External URL',
      type: 'url',
      validation: (Rule) =>
        Rule.uri({
          scheme: ['http', 'https', 'mailto', 'tel'],
        }),
      hidden: ({ parent }) => parent?.linkType !== 'external',
    },
    {
      name: 'anchor',
      title: 'Anchor',
      type: 'string',
      description: 'Add a hash anchor (e.g., #section-name)',
    },
    {
      name: 'openInNewTab',
      title: 'Open in New Tab',
      type: 'boolean',
      initialValue: false,
    },
  ],
  preview: {
    select: {
      linkType: 'linkType',
      internalTitle: 'internalLink.title',
      externalUrl: 'externalUrl',
    },
    prepare({ linkType, internalTitle, externalUrl }) {
      const title = linkType === 'internal' ? internalTitle : externalUrl
      return {
        title: title || 'Link',
        subtitle: linkType === 'internal' ? 'Internal link' : 'External link',
      }
    },
  },
})
