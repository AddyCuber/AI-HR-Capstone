export interface AnimationStep {
  timeline: number;
  bubble_position: { x: number; y: number };
  highlight_area?: { x: number; y: number; width: number; height: number };
  tag_text?: string;
  animation_action: 'move' | 'pause' | 'glow' | 'tag_popout' | 'beam_transfer' | 'complete';
  section_type?: 'name' | 'contact' | 'skills' | 'experience' | 'education';
}

export interface PDFSection {
  type: 'name' | 'contact' | 'skills' | 'experience' | 'education';
  text: string;
  boundingBox: { x: number; y: number; width: number; height: number };
  confidence: number;
}

export function generateAnimationStoryboard(
  pdfSections: PDFSection[],
  pdfDimensions: { width: number; height: number }
): AnimationStep[] {
  const storyboard: AnimationStep[] = [];
  let currentTime = 0;
  const timePerSection = 30000; // 30 seconds per section (much much slower)
  const moveTime = 8000; // 8 seconds for movement (much much slower)
  const pauseTime = 12000; // 12 seconds pause (much much slower)
  const glowTime = 8000; // 8 seconds glow (much much slower)
  const tagTime = 4000; // 4 seconds for tag popout (slower)
  const beamTime = 4000; // 4 seconds for beam transfer (slower)

  // Initial movement to first section
  if (pdfSections.length > 0) {
    const firstSection = pdfSections[0];
    storyboard.push({
      timeline: currentTime,
      bubble_position: { 
        x: firstSection.boundingBox.x + firstSection.boundingBox.width / 2, 
        y: firstSection.boundingBox.y + firstSection.boundingBox.height / 2 
      },
      animation_action: 'move'
    });
    currentTime += moveTime;
  }

  // Process each section
  pdfSections.forEach((section, index) => {
    const centerX = section.boundingBox.x + section.boundingBox.width / 2;
    const centerY = section.boundingBox.y + section.boundingBox.height / 2;

    // Move to section
    storyboard.push({
      timeline: currentTime,
      bubble_position: { x: centerX, y: centerY },
      animation_action: 'move'
    });
    currentTime += moveTime;

    // Pause and highlight
    storyboard.push({
      timeline: currentTime,
      bubble_position: { x: centerX, y: centerY },
      highlight_area: section.boundingBox,
      tag_text: getTagText(section.type),
      animation_action: 'pause',
      section_type: section.type
    });
    currentTime += pauseTime;

    // Glow effect
    storyboard.push({
      timeline: currentTime,
      bubble_position: { x: centerX, y: centerY },
      highlight_area: section.boundingBox,
      tag_text: getTagText(section.type),
      animation_action: 'glow',
      section_type: section.type
    });
    currentTime += glowTime;

    // Tag popout
    storyboard.push({
      timeline: currentTime,
      bubble_position: { x: centerX, y: centerY },
      tag_text: getTagText(section.type),
      animation_action: 'tag_popout',
      section_type: section.type
    });
    currentTime += tagTime;

    // Beam transfer
    storyboard.push({
      timeline: currentTime,
      bubble_position: { x: centerX, y: centerY },
      animation_action: 'beam_transfer',
      section_type: section.type
    });
    currentTime += beamTime;

    // Move to next section (if not the last one)
    if (index < pdfSections.length - 1) {
      const nextSection = pdfSections[index + 1];
      const nextCenterX = nextSection.boundingBox.x + nextSection.boundingBox.width / 2;
      const nextCenterY = nextSection.boundingBox.y + nextSection.boundingBox.height / 2;

      // Create smooth curved path
      const pathSteps = createCurvedPath(
        { x: centerX, y: centerY },
        { x: nextCenterX, y: nextCenterY },
        3 // number of intermediate points
      );

      pathSteps.forEach((point, pathIndex) => {
        storyboard.push({
          timeline: currentTime + (pathIndex * 100),
          bubble_position: point,
          animation_action: 'move'
        });
      });

      currentTime += 300; // Time for curved movement
    }
  });

  // Completion step
  storyboard.push({
    timeline: currentTime,
    bubble_position: { 
      x: pdfDimensions.width / 2, 
      y: pdfDimensions.height / 2 
    },
    animation_action: 'complete'
  });

  return storyboard;
}

function getTagText(sectionType: string): string {
  switch (sectionType) {
    case 'name':
      return 'Name Detected';
    case 'contact':
      return 'Contact Extracted';
    case 'skills':
      return 'Skills Identified';
    case 'experience':
      return 'Experience Analyzed';
    case 'education':
      return 'Education Verified';
    default:
      return 'Section Detected';
  }
}

function createCurvedPath(
  start: { x: number; y: number },
  end: { x: number; y: number },
  steps: number
): Array<{ x: number; y: number }> {
  const path: Array<{ x: number; y: number }> = [];
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = start.x + (end.x - start.x) * t;
    const y = start.y + (end.y - start.y) * t;
    
    // Add slight curve using sine wave
    const curveOffset = Math.sin(t * Math.PI) * 20;
    path.push({
      x: x + curveOffset,
      y: y + curveOffset
    });
  }
  
  return path;
}

// Function to extract sections from resume data
export function extractPDFSections(resumeData: any): PDFSection[] {
  const sections: PDFSection[] = [];
  
  // Name section (usually at the top)
  if (resumeData.name) {
    sections.push({
      type: 'name',
      text: resumeData.name,
      boundingBox: { x: 100, y: 70, width: 200, height: 30 },
      confidence: 0.95
    });
  }

  // Contact section
  if (resumeData.email || resumeData.phone) {
    sections.push({
      type: 'contact',
      text: `${resumeData.email || ''} ${resumeData.phone || ''}`.trim(),
      boundingBox: { x: 180, y: 110, width: 250, height: 40 },
      confidence: 0.9
    });
  }

  // Skills section
  if (resumeData.skills && resumeData.skills.length > 0) {
    sections.push({
      type: 'skills',
      text: resumeData.skills.join(', '),
      boundingBox: { x: 130, y: 190, width: 300, height: 60 },
      confidence: 0.85
    });
  }

  // Experience section
  if (resumeData.experience && resumeData.experience.length > 0) {
    sections.push({
      type: 'experience',
      text: resumeData.experience.map((exp: any) => exp.role).join(', '),
      boundingBox: { x: 160, y: 290, width: 350, height: 100 },
      confidence: 0.8
    });
  }

  // Education section
  if (resumeData.education && resumeData.education.length > 0) {
    sections.push({
      type: 'education',
      text: resumeData.education.map((edu: any) => edu.degree).join(', '),
      boundingBox: { x: 200, y: 440, width: 280, height: 80 },
      confidence: 0.75
    });
  }

  return sections;
}

// Default storyboard for demo purposes
export function getDefaultStoryboard(): AnimationStep[] {
  return [
    // Initial movement to top-left
    { timeline: 0, bubble_position: { x: 50, y: 50 }, animation_action: 'move' },
    
    // Name detection
    { 
      timeline: 500, 
      bubble_position: { x: 120, y: 80 }, 
      highlight_area: { x: 100, y: 70, width: 200, height: 30 },
      tag_text: 'Name Detected',
      animation_action: 'pause',
      section_type: 'name'
    },
    { 
      timeline: 1000, 
      bubble_position: { x: 120, y: 80 }, 
      highlight_area: { x: 100, y: 70, width: 200, height: 30 },
      tag_text: 'Name Detected',
      animation_action: 'glow',
      section_type: 'name'
    },
    { 
      timeline: 1500, 
      bubble_position: { x: 120, y: 80 }, 
      tag_text: 'Name Detected',
      animation_action: 'tag_popout',
      section_type: 'name'
    },
    { 
      timeline: 2000, 
      bubble_position: { x: 120, y: 80 }, 
      animation_action: 'beam_transfer',
      section_type: 'name'
    },

    // Contact info detection
    { 
      timeline: 2500, 
      bubble_position: { x: 200, y: 120 }, 
      highlight_area: { x: 180, y: 110, width: 250, height: 40 },
      tag_text: 'Contact Extracted',
      animation_action: 'pause',
      section_type: 'contact'
    },
    { 
      timeline: 3000, 
      bubble_position: { x: 200, y: 120 }, 
      highlight_area: { x: 180, y: 110, width: 250, height: 40 },
      tag_text: 'Contact Extracted',
      animation_action: 'glow',
      section_type: 'contact'
    },
    { 
      timeline: 3500, 
      bubble_position: { x: 200, y: 120 }, 
      tag_text: 'Contact Extracted',
      animation_action: 'tag_popout',
      section_type: 'contact'
    },
    { 
      timeline: 4000, 
      bubble_position: { x: 200, y: 120 }, 
      animation_action: 'beam_transfer',
      section_type: 'contact'
    },

    // Skills detection
    { 
      timeline: 4500, 
      bubble_position: { x: 150, y: 200 }, 
      highlight_area: { x: 130, y: 190, width: 300, height: 60 },
      tag_text: 'Skills Identified',
      animation_action: 'pause',
      section_type: 'skills'
    },
    { 
      timeline: 5000, 
      bubble_position: { x: 150, y: 200 }, 
      highlight_area: { x: 130, y: 190, width: 300, height: 60 },
      tag_text: 'Skills Identified',
      animation_action: 'glow',
      section_type: 'skills'
    },
    { 
      timeline: 5500, 
      bubble_position: { x: 150, y: 200 }, 
      tag_text: 'Skills Identified',
      animation_action: 'tag_popout',
      section_type: 'skills'
    },
    { 
      timeline: 6000, 
      bubble_position: { x: 150, y: 200 }, 
      animation_action: 'beam_transfer',
      section_type: 'skills'
    },

    // Experience detection
    { 
      timeline: 6500, 
      bubble_position: { x: 180, y: 300 }, 
      highlight_area: { x: 160, y: 290, width: 350, height: 100 },
      tag_text: 'Experience Analyzed',
      animation_action: 'pause',
      section_type: 'experience'
    },
    { 
      timeline: 7000, 
      bubble_position: { x: 180, y: 300 }, 
      highlight_area: { x: 160, y: 290, width: 350, height: 100 },
      tag_text: 'Experience Analyzed',
      animation_action: 'glow',
      section_type: 'experience'
    },
    { 
      timeline: 7500, 
      bubble_position: { x: 180, y: 300 }, 
      tag_text: 'Experience Analyzed',
      animation_action: 'tag_popout',
      section_type: 'experience'
    },
    { 
      timeline: 8000, 
      bubble_position: { x: 180, y: 300 }, 
      animation_action: 'beam_transfer',
      section_type: 'experience'
    },

    // Education detection
    { 
      timeline: 8500, 
      bubble_position: { x: 220, y: 450 }, 
      highlight_area: { x: 200, y: 440, width: 280, height: 80 },
      tag_text: 'Education Verified',
      animation_action: 'pause',
      section_type: 'education'
    },
    { 
      timeline: 9000, 
      bubble_position: { x: 220, y: 450 }, 
      highlight_area: { x: 200, y: 440, width: 280, height: 80 },
      tag_text: 'Education Verified',
      animation_action: 'glow',
      section_type: 'education'
    },
    { 
      timeline: 9500, 
      bubble_position: { x: 220, y: 450 }, 
      tag_text: 'Education Verified',
      animation_action: 'tag_popout',
      section_type: 'education'
    },
    { 
      timeline: 10000, 
      bubble_position: { x: 220, y: 450 }, 
      animation_action: 'beam_transfer',
      section_type: 'education'
    },

    // Completion
    { 
      timeline: 10500, 
      bubble_position: { x: 300, y: 250 }, 
      animation_action: 'complete'
    }
  ];
} 