package com.duoec.video.controller;

import com.duoec.base.core.util.JsonUtils;
import com.duoec.base.dto.response.BaseResponse;
import com.duoec.video.dto.request.*;
import com.duoec.video.jy.JianyingBuilder;
import com.duoec.video.jy.JianyingProjectBuildState;
import com.duoec.video.jy.service.impl.StorageServiceImpl;
import com.duoec.video.project.VideoProject;
import com.duoec.video.project.material.TextStyle;
import com.fasterxml.jackson.core.type.TypeReference;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * PDD春节加班视频 v2 — 一图多句 + 表情包穿插 + 召回BGM
 *
 * 分镜脚本（8句，4图+2表情包）：
 * 图1: "拼多多春节不放假" + "员工直接炸锅了"          → hook
 * 图2: "别人在家吃年夜饭" + "他们在工位上过除夕"      → 爆料
 * 表情包: shocked_2.gif                              → 震惊反应
 * 图3: "加班到凌晨三点" + "年终奖还给砍了"            → 利益点
 * 表情包: tired_2.gif                                → 加班累
 * 图4: "某脉上全是吐槽帖" + "打工人看完沉默了"        → 引导
 *
 * BGM: comical.mp3（搞笑+吐槽，114s）
 */
@SpringBootTest(classes = com.duoec.video.TestConfiguration.class)
@AutoConfigureMockMvc
class PddSpringV2Test {
    static {
        JianyingBuilder.storageService = new StorageServiceImpl();
        JianyingProjectBuildState.DEBUG_JY_DRAFT_DIR = "/root/dreamX/tmp/jy-drafts/";
    }

    @Autowired
    private MockMvc mockMvc;

    private static final long PROJECT_ID = 200004L;
    private static final String SALE_PATH = "file:///root/dreamX/doc/sale/pdd_spring/";
    private static final String MEME_PATH = "file:///root/dreamX/doc/memes/";
    private static final String BGM_PATH = "file:///root/dreamX/doc/bgm/funny/comical.mp3";

    // 8句字幕 + 时长（ms）
    private static final String[] SUBTITLES = {
            "拼多多春节不放假",       // 图1-句1
            "员工直接炸锅了",         // 图1-句2
            "别人在家吃年夜饭",       // 图2-句1
            "他们在工位上过除夕",     // 图2-句2
            "加班到凌晨三点",         // 图3-句1
            "年终奖还给砍了",         // 图3-句2
            "某脉上全是吐槽帖",       // 图4-句1
            "打工人看完沉默了",       // 图4-句2
    };

    // 每句时长（ms）：字数 × 200，最低 1500
    private static final long[] SUB_DURATIONS = {
            1800,  // 9字 × 200 = 1800
            1500,  // 7字 × 200 = 1400 → 1500
            1800,  // 9字 × 200 = 1800
            2000,  // 10字 × 200 = 2000
            1500,  // 7字 × 200 = 1400 → 1500
            1500,  // 7字 × 200 = 1400 → 1500
            1800,  // 9字 × 200 = 1800
            1600,  // 8字 × 200 = 1600
    };

    // 表情包时长
    private static final long MEME_DURATION = 1500;

    // 计算各段 startTime
    // 图1: sub0 + sub1
    // 图2: sub2 + sub3
    // meme1 (shocked)
    // 图3: sub4 + sub5
    // meme2 (tired)
    // 图4: sub6 + sub7

    private long img1Start() { return 0; }
    private long img1Duration() { return SUB_DURATIONS[0] + SUB_DURATIONS[1]; }

    private long img2Start() { return img1Start() + img1Duration(); }
    private long img2Duration() { return SUB_DURATIONS[2] + SUB_DURATIONS[3]; }

    private long meme1Start() { return img2Start() + img2Duration(); }

    private long img3Start() { return meme1Start() + MEME_DURATION; }
    private long img3Duration() { return SUB_DURATIONS[4] + SUB_DURATIONS[5]; }

    private long meme2Start() { return img3Start() + img3Duration(); }

    private long img4Start() { return meme2Start() + MEME_DURATION; }
    private long img4Duration() { return SUB_DURATIONS[6] + SUB_DURATIONS[7]; }

    private long totalDuration() { return img4Start() + img4Duration(); }

    // 字幕 startTime
    private long subStart(int idx) {
        long t = 0;
        // 图1
        if (idx == 0) return img1Start();
        if (idx == 1) return img1Start() + SUB_DURATIONS[0];
        // 图2
        if (idx == 2) return img2Start();
        if (idx == 3) return img2Start() + SUB_DURATIONS[2];
        // 图3
        if (idx == 4) return img3Start();
        if (idx == 5) return img3Start() + SUB_DURATIONS[4];
        // 图4
        if (idx == 6) return img4Start();
        if (idx == 7) return img4Start() + SUB_DURATIONS[6];
        return 0;
    }

    @Test
    void testBuildPddSpringV2() throws Exception {
        long total = totalDuration();
        System.out.println("=== PDD春节加班 v2 ===");
        System.out.println("总时长: " + total + "ms (" + (total / 1000.0) + "s)");

        // 1. 创建项目
        CreateProjectRequest createReq = new CreateProjectRequest();
        createReq.setProjectId(PROJECT_ID);
        createReq.setProjectName("PDD春节加班_v2_一图多句");
        createReq.setWidth(1080);
        createReq.setHeight(1920);
        callApi("/api/project", createReq, "1. 创建项目");

        // 2-7. 图片+表情包（严格按分镜时间顺序穿插）
        addImage(200301L, SALE_PATH + "1.jpg", img1Start(), img1Duration(), "2. 图1 (hook)");
        addImage(200302L, SALE_PATH + "2.jpg", img2Start(), img2Duration(), "3. 图2 (爆料)");
        addImage(200311L, MEME_PATH + "shocked/shocked_2.gif", meme1Start(), MEME_DURATION, "4. 表情包-震惊");
        addImage(200303L, SALE_PATH + "3.jpg", img3Start(), img3Duration(), "5. 图3 (利益点)");
        addImage(200312L, MEME_PATH + "tired/tired_2.gif", meme2Start(), MEME_DURATION, "6. 表情包-加班累");
        addImage(200304L, SALE_PATH + "4.jpg", img4Start(), img4Duration(), "7. 图4 (引导)");

        // 8. 添加背景音乐（召回的 comical.mp3）
        AddAudioRequest bgm = new AddAudioRequest();
        bgm.setProjectId(PROJECT_ID);
        bgm.setScriptIndex(0);
        bgm.setAudioId(200400L);
        bgm.setAudioUrl(BGM_PATH);
        bgm.setStartTime(0L);
        bgm.setDuration(total);
        bgm.setMaterialTimeStart(0L);
        bgm.setMaterialTimeEnd(114500L);
        bgm.setVolume(-30);
        bgm.setFadeInDuration(1000);
        bgm.setFadeOutDuration(1000);
        callApi("/api/project/audio", bgm, "8. BGM (Comical)");

        // 9-16. 添加8条配音
        for (int i = 0; i < 8; i++) {
            AddAudioRequest vo = new AddAudioRequest();
            vo.setProjectId(PROJECT_ID);
            vo.setScriptIndex(0);
            vo.setAudioId(200401L + i);
            vo.setAudioUrl(SALE_PATH + "voiceover_" + (i + 1) + ".mp3");
            vo.setStartTime(subStart(i));
            vo.setDuration(SUB_DURATIONS[i]);
            vo.setVolume(0);
            callApi("/api/project/audio", vo, (9 + i) + ". 配音" + (i + 1));
        }

        // 17-24. 添加8条字幕（统一样式：FFDE00 + 黑色描边）
        for (int i = 0; i < 8; i++) {
            addSubtitle(SUBTITLES[i], subStart(i), SUB_DURATIONS[i],
                    (17 + i) + ". 字幕: " + SUBTITLES[i]);
        }

        // 25. 添加水印
        AddTextRequest watermark = new AddTextRequest();
        watermark.setProjectId(PROJECT_ID);
        watermark.setScriptIndex(0);
        watermark.setText("职场真相");
        watermark.setStartTime(0L);
        watermark.setDuration(total);
        watermark.setPositionX(0);
        watermark.setPositionY(-800);
        watermark.setStyle(new TextStyle()
                .setFontSize(6)
                .setBold(true)
                .setTextAlign(1)
                .setFontName("抖音美好体")
                .setFillColor("#FFFFFF")
                .setStrokeColor("#D61400")
                .setStrokeWidth(60));
        callApi("/api/project/text", watermark, "25. 水印");

        // 26. 构建工程
        BuildProjectRequest buildReq = new BuildProjectRequest();
        buildReq.setProjectId(PROJECT_ID);
        buildReq.setVideoId(PROJECT_ID);

        MvcResult buildResult = mockMvc.perform(post("/api/project/build")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(JsonUtils.toJsonString(buildReq)))
                .andExpect(status().isOk())
                .andReturn();
        BaseResponse<Long> buildResp = JsonUtils.toObject(
                buildResult.getResponse().getContentAsString(), new TypeReference<>() {});
        assertEquals(0, buildResp.getCode());
        assertNotNull(buildResp.getData());

        long taskId = buildResp.getData();
        System.out.println("26. 构建成功! taskId: " + taskId);

        // 读取 COS URL
        java.io.File taskFile = new java.io.File("tmp/task_0/" + taskId + ".json");
        if (taskFile.exists()) {
            String taskJson = new String(java.nio.file.Files.readAllBytes(taskFile.toPath()));
            System.out.println("=== COS 下载链接 ===");
            System.out.println(taskJson);
        }
    }

    private void addImage(long imageId, String imageUrl, long startTime, long duration, String msg) throws Exception {
        AddImageRequest img = new AddImageRequest();
        img.setProjectId(PROJECT_ID);
        img.setScriptIndex(0);
        img.setImageId(imageId);
        img.setImageUrl(imageUrl);
        img.setStartTime(startTime);
        img.setDuration(duration);
        img.setZoomX(10000);
        img.setZoomY(10000);
        img.setPositionX(0);
        img.setPositionY(0);
        callApi("/api/project/image", img, msg);
    }

    private void addSubtitle(String text, long startTime, long duration, String msg) throws Exception {
        AddTextRequest textReq = new AddTextRequest();
        textReq.setProjectId(PROJECT_ID);
        textReq.setScriptIndex(0);
        textReq.setText(text);
        textReq.setStartTime(startTime);
        textReq.setDuration(duration);
        textReq.setPositionX(0);
        textReq.setPositionY(-750);
        textReq.setAsSubtitle(true);
        textReq.setStyle(new TextStyle()
                .setFontSize(8)
                .setBold(true)
                .setTextAlign(1)
                .setFontName("抖音美好体")
                .setFillColor("#FFDE00")
                .setStrokeColor("#000000")
                .setStrokeWidth(60));
        callApi("/api/project/text", textReq, msg);
    }

    private void callApi(String path, Object request, String msg) throws Exception {
        MvcResult result = mockMvc.perform(post(path)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(JsonUtils.toJsonString(request)))
                .andExpect(status().isOk())
                .andReturn();
        BaseResponse<?> resp = JsonUtils.toObject(
                result.getResponse().getContentAsString(), new TypeReference<BaseResponse<Object>>() {});
        assertEquals(0, resp.getCode(), "Failed: " + msg);
        System.out.println("✅ " + msg);
    }
}
