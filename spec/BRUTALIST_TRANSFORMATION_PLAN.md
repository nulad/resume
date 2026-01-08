# Brutalist Design Transformation Plan

## Project Overview
Transform the Jekyll resume repository to adopt the pure brutalist design system from nulad.github.io while maintaining the existing Jekyll architecture and content structure.

## Design System Analysis

### Core Brutalist Elements to Implement
1. **Color Palette**
   - Pure black (#000000) for text and borders
   - Pure white (#ffffff) for backgrounds
   - No gradients or shades

2. **Typography**
   - Monospace font stack: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas
   - Font weights: 700 (bold) for headers, normal for body
   - No smooth font rendering hints

3. **Border System**
   - Thin borders: 2px
   - Standard borders: 3px
   - Thick borders: 4px
   - Heavy borders: 5px
   - No rounded corners

4. **Transitions & Animations**
   - Complete removal of all transitions
   - No hover animations
   - Instant state changes

5. **Layout Characteristics**
   - Heavy borders on all interactive elements
   - Boxed headers with black backgrounds
   - High contrast throughout
   - Rigid, geometric spacing

## Implementation Strategy

### Phase 1: Foundation Updates
**Files to Modify:**
1. `_sass/_variables.scss`
   - Replace color variables
   - Update font stacks
   - Define border widths
   - Set spacing scale

2. `_sass/_mixins.scss`
   - Remove transition mixins
   - Add brutalist border utilities
   - Create responsive breakpoints
   - Add print style mixins

### Phase 2: Base Styling
**Files to Modify:**
3. `_sass/_base.scss`
   - Reset styles for brutalist design
   - Typography (h1-h6, p, a)
   - List styling with square bullets
   - Code blocks with heavy borders
   - Form elements

### Phase 3: Layout System
**Files to Modify:**
4. `_sass/_layout.scss`
   - Container with thick borders
   - Section layouts with borders
   - Grid system adjustments
   - Responsive utilities

### Phase 4: Component Transformation
**Files to Modify:**
5. `_sass/_resume.scss`
   - Section headers with black backgrounds
   - Page header with bordered avatar
   - Contact button with brutalist style
   - Resume items with heavy borders
   - Icon links with borders
   - Footer redesign

## Detailed File Modification Plan

### 1. _variables.scss Changes
- Remove existing color variables
- Add brutalist color system
- Update font stacks to monospace
- Define border width variables
- Create spacing scale
- Add transition disable variable

### 2. _mixins.scss Changes
- Remove all transition-based mixins
- Add border utility mixins
- Create brutalist hover effects
- Add responsive media query mixins
- Include print style mixins

### 3. _base.scss Changes
- Implement universal transition disable
- Redesign typography with borders
- Style links with underline and hover states
- Create brutalist list styles
- Style code blocks with heavy borders
- Form element redesign

### 4. _layout.scss Changes
- Wrapper with thick border
- Section containers with borders
- Responsive grid adjustments
- Spacing utilities
- Mobile-first responsive design

### 5. _resume.scss Changes
- Section headers as black boxes
- Avatar with thick border
- Name as black-bordered box
- Contact button with brutalist style
- Resume items with borders
- Print style preservation

## Responsive Design Strategy

### Mobile Adaptations
- Reduce border widths on small screens
- Adjust font sizes for readability
- Stack elements vertically
- Maintain brutalist aesthetic

### Breakpoints
- Mobile: ≤ 768px
- Tablet: 769px - 1024px
- Desktop: ≥ 1025px

### Mobile Considerations
- Thinner borders to save space
- Smaller font sizes but maintain hierarchy
- Touch-friendly interactive elements
- Preserve all brutalist elements

## Testing & Validation Checklist

### Visual Validation
- [ ] All text uses monospace fonts
- [ ] Pure black/white color scheme
- [ ] Heavy borders on all elements
- [ ] No rounded corners anywhere
- [ ] No transitions or animations

### Functional Testing
- [ ] All links work with hover states
- [ ] Contact button functions properly
- [ ] Print styles maintain readability
- [ ] Social icons display correctly

### Responsive Testing
- [ ] Mobile layout works correctly
- [ ] Tablet adaptation successful
- [ ] Desktop layout as intended
- [ ] Border scaling appropriate

### Cross-browser Testing
- [ ] Chrome compatibility
- [ ] Firefox compatibility
- [ ] Safari compatibility
- [ ] Edge compatibility

## Implementation Timeline

### Immediate Actions (Day 1)
1. Backup current styles
2. Update variables file
3. Modify mixins
4. Update base styles

### Secondary Actions (Day 1-2)
5. Transform layout system
6. Redesign resume components
7. Test responsive behavior

### Finalization (Day 2)
8. Validate all functionality
9. Test print styles
10. Cross-browser verification
11. Performance optimization

## Risk Mitigation

### Potential Issues
1. Print readability with heavy borders
2. Mobile usability with thick borders
3. Font rendering across browsers

### Solutions
1. Special print media queries with thinner borders
2. Responsive border scaling
3. Font stack optimization

## Success Criteria

1. Visual design matches nulad.github.io brutalist style
2. All resume content remains accessible
3. Responsive design works on all devices
4. Print functionality preserved
5. Site performance maintained

## Implementation Commands

### Backup Current Styles
```bash
cp -r _sass _sass_backup
cp css/main.scss css/main.scss.backup
```

### Build and Serve
```bash
bundle exec jekyll build
bundle exec jekyll serve
```

### Validate Changes
```bash
# Check compiled CSS
grep -E "(border:|font-family:|color:|background:)" css/main.css | head -20
```

## Notes
- This transformation maintains the Jekyll architecture
- All content structure remains unchanged
- Print functionality is preserved with special media queries
- Responsive design is prioritized for mobile devices
- Performance impact is minimal with pure CSS changes
