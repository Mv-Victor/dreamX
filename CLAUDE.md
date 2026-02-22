# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Duo-Video is a Java video editing SDK that generates professional video projects programmatically through a clean API. It uses a layered architecture to create JianYing (剪映) project files for video production.

**Tech Stack**: Java 21, Spring Boot 3.5.8, Maven

## Build & Development Commands

### Build
```bash
mvn clean install          # Build all modules
mvn clean package         # Package without installing
mvn clean test            # Run all tests
```

### Run API Server
```bash
cd duo-video-api
mvn spring-boot:run       # Starts on http://localhost:8080
```

### Run Single Test
```bash
mvn test -Dtest=ClassName#methodName
# Example: mvn test -Dtest=JianyingBuilderTest#buildWithProjectJson
```

### Module-Specific Build
```bash
cd duo-video-jy           # Or any module
mvn clean install
```

## Architecture

### Module Structure

```
duo-video/
├── duo-video-base/       # Core data models (VideoProject, Material, Segment)
├── duo-video-jy/         # JianYing format conversion (17 Builder classes)
├── duo-video-api/        # REST API layer (Spring Boot)
└── duo-server-base/      # Shared utilities (JSON, file handling, ID generation)
```

### Core Data Flow

```
VideoProject (JSON) → JianyingBuilder → JianYingProjectInfo (draft files) → AutoJY → Video Export
```

### Key Classes

**duo-video-base**:
- `VideoProject`: Root container (scripts, materials, dimensions, fps)
- `VideoScript`: Scene/shot container (segments list, optional time constraint)
- `VideoSegment`: Individual element (materialId, time, position, effects)
- `BaseMaterial`: Abstract material (VideoMaterial, ImageMaterial, TextMaterial, etc.)
- `ProjectBuilder`: Fluent API entry point for building projects

**duo-video-jy**:
- `JianyingBuilder`: Main conversion orchestrator (VideoProject → JianYing format)
- `JianyingProjectBuildState`: Conversion context (material maps, caching, file management)
- `JianyingMaterialBuilder`: Downloads materials, extracts metadata via FFmpeg
- `JianyingSegmentBuilder`: Dispatcher routing to type-specific builders
- `SegmentBuilder<T>`: Interface for polymorphic segment conversion (VideoSegmentBuilder, TextSegmentBuilder, etc.)
- `JianyingScriptBuilder`: Script-level conversion
- `JianyingTrackBuilder`: Track management and ordering

**duo-video-api**:
- `VideoProjectService`: Business logic interface
- `VideoProjectApiController`: REST endpoints at `/api/project`
- Request DTOs: `AddVideoRequest`, `AddTextRequest`, etc.

### Builder Pattern

The codebase uses nested builders extensively:

```java
ProjectBuilder.createBuilder(id, name, width, height)
    .buildScript(0, scriptBuilder -> {
        scriptBuilder
            .buildNewVideo(videoId, url, start, duration, videoBuilder -> {
                videoBuilder.setSpeed(50).setPosition(0, -400);
            })
            .buildNewText(text, start, duration, textBuilder -> {
                textBuilder.setStyle(style).setPosition(0, 1866);
            });
    })
    .getProject();
```

Each builder has:
- `back()`: Return to parent builder
- `build(Consumer<Builder>)`: Functional style configuration
- Type-specific setters for properties

### Material Type Hierarchy

```
BaseMaterial
├── BaseVisibleMediaMaterial (width, height, localFile)
│   ├── VideoMaterial (time range, greenBackground, lut)
│   └── ImageMaterial
├── AudioMaterial
├── TextMaterial (text, style, words for per-character styling)
├── TextTemplateMaterial (resourceId, texts array)
├── StickerMaterial (resourceId)
├── TransitionMaterial (resourceId)
├── VideoEffectMaterial (resourceId)
├── FaceEffectMaterial (resourceId)
├── MaskMaterial (resourceId, config)
├── LutMaterial (url)
└── StyleMaterial (style, globalKeywordStyle flag)
```

### Coordinate System

```
        Y+
        ↑
        |
X- ←--(0,0)--→ X+
        |
        ↓
        Y-
```

- Origin (0,0): Video canvas center
- X-axis: Left negative, right positive
- Y-axis: Up positive, down negative (inverted from typical)

### Time Units

All time values use **milliseconds**:
- 1 second = 1,000 ms
- 3 seconds = 3,000 ms

### Track Layer Order (Bottom to Top)

1. Sound effects (特效音)
2. Audio (音频)
3. Green screen background (绿幕背景)
4. Video (视频)
5. Image (图片)
6. Mask (蒙板)
7. Video effects (画面特效)
8. Sticker (贴纸)
9. Subtitle (字幕)
10. Text (文本)
11. Text template (文本模板)

Higher `layoutIndex` = rendered on top.

## Configuration

### Test Configuration

Before running tests, update the JianYing draft directory in `duo-video-jy/src/test/java/com/duoec/video/jy/BaseTest.java`:

```java
JianyingProjectBuildState.DEBUG_JY_DRAFT_DIR = "/path/to/your/JianyingPro/User Data/Projects/com.lveditor.draft/";
```

### Environment Variables (Optional)

For accessing non-public resources:

| Variable | Description | Default |
|----------|-------------|---------|
| DUO_SECRET_ID | API signature secret ID | (public access only) |
| DUO_SECRET_KEY | API signature secret key | (public access only) |
| DUO_SERVER | Resource server URL | https://api.duoec.com/api/jy/resource/ |

### Cache Directory

Default cache: `duo-video-jy/tmp/`

If encountering errors, try clearing this directory.

## Dependencies

### FFmpeg

Required for video processing (metadata extraction, reversal, segment caching).

Install: https://www.ffmpeg.org/download.html

Ensure `ffmpeg` is in PATH.

### Exiftool (Optional)

Used for additional media metadata extraction.

## Common Patterns

### Creating VideoProject from JSON

```java
VideoProject project = FileUtils.readJson("001_base_project.json", VideoProject.class);
JianYingProjectInfo jyProject = new JianyingBuilder().build(project);
```

Test JSON files are in `duo-video-jy/src/test/resources/`.

### Green Screen + Background

```java
VideoMaterial video = new VideoMaterial()
    .setGreenBackground(new GreenBackground()
        .setMaterialId(backgroundId)
        .setBaseBackgroundColor("#4e8a1fff")
        .setStrength(20)
        .setEdgeFeather(10)
        .setEdgeCleanup(10));
```

Creates composite segment combining video + background with chroma key.

### Text with Per-Word Styling

```java
TextMaterial text = new TextMaterial()
    .setText("测试中文字幕")
    .setStyle(globalStyle)
    .setWords(List.of(
        new TextWord().setIndex(2).setLength(2).setFillColor("#00FFFF"),
        new TextWord().setIndex(3).setLength(2).setFontSize(18)
    ));
```

### Combining Segments into Composite Clip

```java
JianyingUtils.combine(projectInfo, List.of(segment1, segment2));
```

Merges segments and their materials into a composite clip (like JianYing's merge feature).

### Material Caching

Video segments are cached by `materialId_backgroundId` to avoid duplication when the same material is reused.

### Reference System

Segments can reference other materials via `refs` map:

```java
segment.setRefs(Map.of(
    transitionId, "transition",
    maskId, "mask"
));
```

## API Usage

### Create Project

```bash
POST /api/project
{
  "projectId": 123456789,
  "projectName": "My Video",
  "width": 1080,
  "height": 1920,
  "test": true
}
```

### Add Video with Green Screen

```bash
POST /api/project/video
{
  "projectId": 123456789,
  "videoId": 535010997887571021,
  "videoUrl": "https://example.com/video.mp4",
  "startTime": 0,
  "duration": 3000,
  "greenBackground": {
    "greenScreenId": 535010997887571022,
    "greenScreenUrl": "https://example.com/bg.png",
    "chromaColor": "#4e8a1fff",
    "chromaStrength": 20
  }
}
```

### Add Text with Styling

```bash
POST /api/project/text
{
  "projectId": 123456789,
  "text": "Hello World",
  "startTime": 0,
  "duration": 3000,
  "style": {
    "fontSize": 14,
    "fillColor": "#FFFFFF",
    "strokeColor": "#FF0000",
    "strokeWidth": 10
  }
}
```

Full API documentation in README.md section 6.5.

## Important Notes

### Material IDs

Material IDs must be globally unique integers. They're used as temporary filenames during JianYing conversion. Duplicate IDs will cause incorrect video references.

Use `SnowflakeIdUtils.nextTmpId()` for generation.

### Speed Units

Speed is in percentage: 100 = 1x, 50 = 0.5x, 200 = 2x.

### Zoom Units

Zoom is in 1/10000: 10000 = 100%, 5000 = 50%, 20000 = 200%.

### Rotation

Positive = clockwise, negative = counterclockwise.

### Video Reversal (倒放)

Set `segment.setUpend(true)`. JianyingMaterialBuilder processes video with FFmpeg to create reversed version.

### Text Templates

Text templates require matching number of text blocks. Resource IDs available at: https://www.duoec.com/video

### Supported JianYing Version

Verified with JianYing Professional v10.1.0. Older versions may not support all features (e.g., vertical mirror, shadow in green screen).

## Troubleshooting

### Clear Cache

If encountering strange errors, delete `duo-video-jy/tmp/` directory.

### Check Logs

The codebase provides detailed error logging. Review console output for specific error messages.

### Test Mode

Set `project.setTest(true)` or `projectBuilder.setTest(true)` to enable test mode, which may provide additional debugging output.

### FFmpeg Issues

Ensure FFmpeg is installed and accessible in PATH. Test with `ffmpeg -version`.
