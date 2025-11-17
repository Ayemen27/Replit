import { defineType } from 'sanity'

export default defineType({
  name: 'commentsSection',
  title: 'Comments Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(100),
      initialValue: 'Comments',
    },
    {
      name: 'enabled',
      title: 'Enable Comments',
      type: 'boolean',
      description: 'Allow users to post comments',
      initialValue: true,
    },
    {
      name: 'moderationRequired',
      title: 'Moderation Required',
      type: 'boolean',
      description: 'Comments must be approved before being published',
      initialValue: false,
    },
    {
      name: 'allowAnonymous',
      title: 'Allow Anonymous Comments',
      type: 'boolean',
      description: 'Allow users to comment without logging in',
      initialValue: false,
    },
    {
      name: 'sortOrder',
      title: 'Default Sort Order',
      type: 'string',
      options: {
        list: [
          { title: 'Newest First', value: 'newest' },
          { title: 'Oldest First', value: 'oldest' },
          { title: 'Most Popular', value: 'popular' },
        ],
        layout: 'radio',
      },
      initialValue: 'newest',
    },
    {
      name: 'maxDepth',
      title: 'Maximum Thread Depth',
      type: 'number',
      description: 'Maximum levels of nested replies (0 = no nesting)',
      validation: (Rule) => Rule.min(0).max(10),
      initialValue: 3,
    },
    {
      name: 'placeholder',
      title: 'Comment Placeholder',
      type: 'string',
      description: 'Placeholder text for comment input',
      initialValue: 'Share your thoughts...',
    },
    {
      name: 'disabledMessage',
      title: 'Disabled Message',
      type: 'text',
      rows: 2,
      description: 'Message to show when comments are disabled',
      initialValue: 'Comments are currently disabled for this content.',
      hidden: ({ parent }) => parent?.enabled !== false,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      enabled: 'enabled',
      moderation: 'moderationRequired',
    },
    prepare({ title, enabled, moderation }) {
      const status = enabled 
        ? (moderation ? 'Enabled (Moderated)' : 'Enabled')
        : 'Disabled'
      return {
        title: title || 'Comments Section',
        subtitle: status,
      }
    },
  },
})
