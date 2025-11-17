import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'navigationMenu',
  title: 'Navigation Menu',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Menu Title',
      type: 'string',
      description: 'Internal reference name for this menu',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'menuItems',
      title: 'Menu Items',
      type: 'array',
      of: [
        {
          type: 'object',
          name: 'menuItem',
          title: 'Menu Item',
          fields: [
            {
              name: 'label',
              title: 'Label',
              type: 'string',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'url',
              title: 'URL',
              type: 'string',
              description: 'Internal path (e.g., /about) or external URL',
            },
            {
              name: 'openInNewTab',
              title: 'Open in New Tab',
              type: 'boolean',
              initialValue: false,
            },
            {
              name: 'icon',
              title: 'Icon',
              type: 'string',
              description: 'Icon name or class (optional)',
            },
            {
              name: 'subItems',
              title: 'Sub Items',
              type: 'array',
              of: [
                {
                  type: 'object',
                  name: 'subMenuItem',
                  title: 'Sub Menu Item',
                  fields: [
                    {
                      name: 'label',
                      title: 'Label',
                      type: 'string',
                      validation: (Rule) => Rule.required(),
                    },
                    {
                      name: 'url',
                      title: 'URL',
                      type: 'string',
                      description: 'Internal path or external URL',
                    },
                    {
                      name: 'openInNewTab',
                      title: 'Open in New Tab',
                      type: 'boolean',
                      initialValue: false,
                    },
                    {
                      name: 'icon',
                      title: 'Icon',
                      type: 'string',
                      description: 'Icon name or class (optional)',
                    },
                    {
                      name: 'description',
                      title: 'Description',
                      type: 'string',
                      description: 'Optional description for mega menu',
                    },
                  ],
                  preview: {
                    select: {
                      title: 'label',
                      subtitle: 'url',
                    },
                  },
                },
              ],
            },
            {
              name: 'highlighted',
              title: 'Highlighted',
              type: 'boolean',
              description: 'Highlight this menu item (e.g., with different styling)',
              initialValue: false,
            },
          ],
          preview: {
            select: {
              title: 'label',
              subtitle: 'url',
              hasSubItems: 'subItems',
            },
            prepare({ title, subtitle, hasSubItems }) {
              return {
                title,
                subtitle: hasSubItems && hasSubItems.length > 0 
                  ? `${subtitle} (${hasSubItems.length} sub-items)` 
                  : subtitle,
              }
            },
          },
        },
      ],
    }),
    defineField({
      name: 'ctaButton',
      title: 'CTA Button',
      type: 'object',
      description: 'Call-to-action button in navigation',
      fields: [
        {
          name: 'text',
          title: 'Button Text',
          type: 'string',
        },
        {
          name: 'url',
          title: 'Button URL',
          type: 'string',
        },
        {
          name: 'style',
          title: 'Button Style',
          type: 'string',
          options: {
            list: [
              { title: 'Primary', value: 'primary' },
              { title: 'Secondary', value: 'secondary' },
              { title: 'Outline', value: 'outline' },
            ],
          },
          initialValue: 'primary',
        },
      ],
      options: {
        collapsible: true,
        collapsed: false,
      },
    }),
  ],
  preview: {
    select: {
      title: 'title',
      itemCount: 'menuItems',
    },
    prepare({ title, itemCount }) {
      return {
        title,
        subtitle: itemCount ? `${itemCount.length} menu items` : 'No items',
      }
    },
  },
})
