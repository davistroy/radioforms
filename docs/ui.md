# UI/UX Design Specification
*A Modern Design System for ICS Forms Management Application*

## Table of Contents
1. [Design Philosophy](#design-philosophy)
2. [Technology Foundation](#technology-foundation)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Spacing & Layout](#spacing--layout)
6. [Component Library](#component-library)
7. [Navigation Patterns](#navigation-patterns)
8. [Forms & Inputs](#forms--inputs)
9. [Data Display](#data-display)
10. [Interaction States](#interaction-states)
11. [Responsive Design](#responsive-design)
12. [Implementation Guidelines](#implementation-guidelines)

---

## Design Philosophy

### Core Principles
- **Functional Clarity**: Every element serves a clear purpose for emergency management workflows
- **Responsive Adaptability**: Seamless experience across desktop and tablet devices
- **Modular Architecture**: Reusable components with consistent behavior
- **Accessibility First**: WCAG 2.1 AA compliance for all users
- **Professional Focus**: Clean, business-appropriate design for emergency management professionals

### Visual Approach
- Clean, minimalist interface with purposeful use of whitespace
- Subtle shadows and borders for depth without distraction
- Consistent iconography using Lucide React icons
- Progressive disclosure to manage form complexity
- Focus on data clarity and rapid form completion

---

## Technology Foundation

### Design System Stack
- **Styling**: Tailwind CSS for utility-first styling
- **Components**: shadcn/ui for high-quality, accessible base components
- **Icons**: Lucide React for consistent iconography
- **Typography**: Inter font family for excellent readability
- **Dark Mode**: Built-in support with CSS custom properties

### Design Tokens
All design tokens are defined in CSS custom properties and Tailwind configuration:

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
    },
  },
}
```

---

## Color System

### Primary Palette
```css
:root {
  /* Primary Colors - Professional Blue */
  --primary: 214 84% 56%;           /* Main brand color */
  --primary-foreground: 210 40% 98%;
  
  /* Secondary Colors - Neutral Gray */
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 84% 4.9%;
  
  /* Contextual Colors */
  --destructive: 0 84.2% 60.2%;    /* Errors, destructive actions */
  --destructive-foreground: 210 40% 98%;
  
  /* Status Colors */
  --success: 142 76% 36%;          /* Success states */
  --warning: 38 92% 50%;           /* Warnings, cautions */
  --info: 214 84% 56%;             /* Information alerts */
}
```

### Dark Mode Support
```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 84% 4.9%;
  /* Additional dark mode tokens... */
}
```

### Usage Guidelines
- **Primary**: Use for main CTAs, active states, and brand elements
- **Secondary**: Background elements, subtle actions
- **Destructive**: Error states, delete actions, critical warnings
- **Muted**: Secondary text, disabled states, subtle backgrounds

---

## Typography

### Font System
```css
/* Primary Font Family */
font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", 
             Roboto, "Helvetica Neue", Arial, sans-serif;

/* Monospace Font */
font-family: ui-monospace, SFMono-Regular, "SF Mono", Monaco, 
             "Cascadia Code", "Roboto Mono", Consolas, monospace;
```

### Type Scale (Tailwind Classes)
```typescript
// Usage in components
<h1 className="text-4xl font-bold">     // 36px, 900 weight
<h2 className="text-3xl font-semibold"> // 30px, 600 weight
<h3 className="text-2xl font-semibold"> // 24px, 600 weight
<h4 className="text-xl font-medium">    // 20px, 500 weight
<h5 className="text-lg font-medium">    // 18px, 500 weight
<h6 className="text-base font-medium">  // 16px, 500 weight

// Body text
<p className="text-base">               // 16px, 400 weight
<p className="text-sm">                 // 14px, 400 weight
<p className="text-xs">                 // 12px, 400 weight

// Muted text
<p className="text-sm text-muted-foreground">
```

### Text Utilities
```typescript
// Truncation
<p className="truncate">
<p className="text-ellipsis overflow-hidden">

// Line clamping
<p className="line-clamp-2">
<p className="line-clamp-3">
```

---

## Spacing & Layout

### Spacing Scale (Tailwind)
```typescript
// Padding and Margin
p-0    // 0px
p-1    // 4px
p-2    // 8px
p-3    // 12px
p-4    // 16px
p-6    // 24px
p-8    // 32px
p-12   // 48px
p-16   // 64px

// Gap spacing
gap-1  // 4px
gap-2  // 8px
gap-4  // 16px
gap-6  // 24px
```

### Layout Patterns
```typescript
// Card layout
<div className="p-6 bg-card text-card-foreground rounded-lg border shadow-sm">

// Form layout
<div className="space-y-4">
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

// Content spacing
<div className="space-y-6">        // Vertical spacing between sections
<div className="flex items-center gap-2">  // Horizontal spacing
```

### Border Radius
```typescript
rounded-none   // 0px
rounded-sm     // 2px
rounded        // 4px
rounded-md     // 6px
rounded-lg     // 8px
rounded-xl     // 12px
```

---

## Component Library

### Core Components (shadcn/ui)

#### Button Component
```typescript
import { Button } from "@/components/ui/button"

// Primary button
<Button>Save Form</Button>

// Secondary button
<Button variant="secondary">Cancel</Button>

// Destructive button
<Button variant="destructive">Delete</Button>

// Outline button
<Button variant="outline">Export</Button>

// Ghost button
<Button variant="ghost">Close</Button>

// Button sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
```

#### Input Components
```typescript
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

// Basic input
<div className="space-y-2">
  <Label htmlFor="incident-name">Incident Name</Label>
  <Input id="incident-name" placeholder="Enter incident name" />
</div>

// Textarea
<div className="space-y-2">
  <Label htmlFor="description">Description</Label>
  <Textarea id="description" placeholder="Enter description" />
</div>
```

#### Select Component
```typescript
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select form type" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="ICS-201">ICS-201 - Incident Briefing</SelectItem>
    <SelectItem value="ICS-202">ICS-202 - Incident Objectives</SelectItem>
  </SelectContent>
</Select>
```

#### Card Component
```typescript
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Form Details</CardTitle>
    <CardDescription>
      Configure your ICS form settings
    </CardDescription>
  </CardHeader>
  <CardContent>
    {/* Form content */}
  </CardContent>
  <CardFooter>
    <Button>Save</Button>
  </CardFooter>
</Card>
```

### Custom Form Components

#### Form Field Wrapper
```typescript
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"

<FormField
  control={form.control}
  name="incidentName"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Incident Name</FormLabel>
      <FormControl>
        <Input placeholder="Enter incident name" {...field} />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

#### Status Badge
```typescript
import { Badge } from "@/components/ui/badge"

<Badge variant="default">Draft</Badge>
<Badge variant="secondary">Completed</Badge>
<Badge variant="destructive">Error</Badge>
<Badge variant="outline">Archived</Badge>
```

---

## Navigation Patterns

### Main Navigation
```typescript
// Top navigation bar
<header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <div className="container flex h-14 items-center">
    <div className="flex items-center space-x-4">
      <Button variant="ghost" size="sm">
        <Menu className="h-4 w-4" />
      </Button>
      <h1 className="font-semibold">ICS Forms Manager</h1>
    </div>
    
    <div className="ml-auto flex items-center space-x-4">
      <Button variant="ghost" size="sm">
        <Settings className="h-4 w-4" />
      </Button>
    </div>
  </div>
</header>
```

### Sidebar Navigation
```typescript
// Collapsible sidebar
<aside className={cn(
  "border-r bg-muted/40 transition-all duration-300",
  collapsed ? "w-16" : "w-64"
)}>
  <nav className="flex flex-col space-y-2 p-4">
    <Button variant="ghost" className="justify-start">
      <FileText className="h-4 w-4" />
      {!collapsed && <span className="ml-2">Forms</span>}
    </Button>
    <Button variant="ghost" className="justify-start">
      <Archive className="h-4 w-4" />
      {!collapsed && <span className="ml-2">Archive</span>}
    </Button>
  </nav>
</aside>
```

### Breadcrumb Navigation
```typescript
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/forms">Forms</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>ICS-201</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

---

## Forms & Inputs

### Form Layout Patterns
```typescript
// Single column form
<div className="space-y-6">
  <div className="space-y-4">
    {/* Form fields */}
  </div>
</div>

// Two column form
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <FormField />
  <FormField />
</div>

// Complex form with sections
<div className="space-y-8">
  <div>
    <h3 className="text-lg font-medium">Incident Information</h3>
    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Fields */}
    </div>
  </div>
  
  <Separator />
  
  <div>
    <h3 className="text-lg font-medium">Personnel Details</h3>
    <div className="mt-4 space-y-4">
      {/* Fields */}
    </div>
  </div>
</div>
```

### Validation Display
```typescript
// Field-level validation
<FormField
  control={form.control}
  name="email"
  render={({ field, fieldState }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl>
        <Input 
          {...field} 
          className={fieldState.error ? "border-destructive" : ""} 
        />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>

// Form-level validation summary
{form.formState.errors && (
  <Alert variant="destructive">
    <AlertCircle className="h-4 w-4" />
    <AlertTitle>Validation Error</AlertTitle>
    <AlertDescription>
      Please correct the errors below before saving.
    </AlertDescription>
  </Alert>
)}
```

---

## Data Display

### Table Component
```typescript
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Form Type</TableHead>
      <TableHead>Incident Name</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Created</TableHead>
      <TableHead className="text-right">Actions</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>ICS-201</TableCell>
      <TableCell>Mountain Fire</TableCell>
      <TableCell>
        <Badge variant="secondary">Draft</Badge>
      </TableCell>
      <TableCell>2 hours ago</TableCell>
      <TableCell className="text-right">
        <Button variant="ghost" size="sm">Edit</Button>
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Data Cards
```typescript
// Form summary card
<Card>
  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
    <CardTitle className="text-sm font-medium">
      Active Forms
    </CardTitle>
    <FileText className="h-4 w-4 text-muted-foreground" />
  </CardHeader>
  <CardContent>
    <div className="text-2xl font-bold">12</div>
    <p className="text-xs text-muted-foreground">
      +2 from last week
    </p>
  </CardContent>
</Card>
```

---

## Interaction States

### Loading States
```typescript
import { Skeleton } from "@/components/ui/skeleton"

// Button loading
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Saving...
</Button>

// Content loading
<div className="space-y-3">
  <Skeleton className="h-5 w-2/5" />
  <Skeleton className="h-4 w-4/5" />
  <Skeleton className="h-4 w-3/5" />
</div>
```

### Error States
```typescript
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Failed to save form. Please try again.
  </AlertDescription>
</Alert>
```

### Empty States
```typescript
<div className="flex flex-col items-center justify-center py-12">
  <FileX className="h-12 w-12 text-muted-foreground" />
  <h3 className="mt-4 text-lg font-semibold">No forms found</h3>
  <p className="mt-2 text-sm text-muted-foreground">
    Get started by creating your first ICS form.
  </p>
  <Button className="mt-4">
    <Plus className="mr-2 h-4 w-4" />
    Create Form
  </Button>
</div>
```

---

## Responsive Design

### Breakpoint Strategy
```typescript
// Tailwind breakpoints
sm: '640px'   // Small tablets
md: '768px'   // Tablets
lg: '1024px'  // Laptops
xl: '1280px'  // Desktops
2xl: '1536px' // Large desktops
```

### Responsive Patterns
```typescript
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Responsive navigation
<nav className="hidden md:flex items-center space-x-4">
<Button className="md:hidden" variant="ghost" size="sm">
  <Menu className="h-4 w-4" />
</Button>

// Responsive text sizing
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">

// Responsive spacing
<div className="p-4 md:p-6 lg:p-8">
```

---

## Implementation Guidelines

### Component Development
1. **Start with shadcn/ui base components**
2. **Extend with Tailwind utilities for customization**
3. **Create composite components for common patterns**
4. **Ensure proper TypeScript typing**

### Accessibility Requirements
```typescript
// Proper ARIA labels
<Button aria-label="Save form">
  <Save className="h-4 w-4" />
</Button>

// Form associations
<Label htmlFor="incident-name">Incident Name</Label>
<Input id="incident-name" />

// Focus management
<DialogTrigger asChild>
  <Button>Open Form</Button>
</DialogTrigger>
```

### Performance Considerations
1. **Use React.memo for expensive components**
2. **Implement virtual scrolling for large lists**
3. **Lazy load non-critical components**
4. **Optimize image assets**

### Testing Approach
```typescript
// Component testing
import { render, screen } from '@testing-library/react'

test('renders form field correctly', () => {
  render(
    <FormField 
      name="test" 
      label="Test Field" 
      required 
    />
  )
  expect(screen.getByLabelText(/test field/i)).toBeInTheDocument()
})
```

---

This design specification provides a comprehensive foundation for building the ICS Forms Management Application with modern, accessible, and maintainable UI components using React, TypeScript, Tailwind CSS, and shadcn/ui.