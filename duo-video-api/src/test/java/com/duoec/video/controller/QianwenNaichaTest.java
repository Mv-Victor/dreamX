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
 * 千问奶茶事件 — 小红书营销视频
 * 一图多句 + 表情包穿插 + 素材库召回BGM
 *
 * 分镜：
 * 图1: "千问砸30亿请喝奶茶" + "全国人民疯狂涌入"
 * 图2: "服务器直接炸了" + "APP崩了一整天"
 * 表情包: shocked_1.gif（震惊）
 * 图3: "运维小哥连夜加班" + "这波属实格局打开了"
 * 表情包: cat_funny GIF（搞笑）
 * 图4: "网上全是讨论帖" + "评论区比春晚还热闹"
 *
 * BGM: Just Kidding（搞笑+欢快，179s）
 */
@SpringBootTest(classes = com.duoec.video.TestConfiguration.class)
@AutoConfigureMockMvc
class QianwenNaichaTest {
    static {
        JianyingBuilder.storageService = new StorageServiceImpl();
        JianyingProjectBuildState.DEBUG_JY_DRAFT_DIR = "/root/dreamX/tmp/jy-drafts/";
    }

    @Autowired
    private MockMvc mockMvc;

    private static final long PROJECT_ID = 200005L;
    private static final String SALE_PATH = "file:///root/dreamX/doc/sale/qianwen_naicha/";
    private static final String MEME_SHOCKED = "file:///root/dreamX/doc/memes/shocked/shocked_1.gif";
    private static final String MEME_FUNNY = "file:///root/dreamX/doc/memes/stonks/Business_GIF_zaB7dTEHx581vwPHPB.gif";
    private static final String BGM_PATH = "file:///root/dreamX/doc/bgm/funny/just_kidding.mp3";

    private static final String[] SUBTITLES = {
            "千问砸30亿请喝奶茶",   // 图1-句1
            "全国人民疯狂涌入",     // 图1-句2
            "服务器直接炸了",       // 图2-句1
            "APP崩了一整天",       // 图2-句2
            "运维小哥连夜加班",     // 图3-句1
            "这波属实格局打开了",   // 图3-句2
            "网上全是讨论帖",       // 图4-句1
            "评论区比春晚还热闹",   // 图4-句2
    };

    // 每句时长（ms）：字数 × 200，最低 1500
    private static final long[] SUB_DUR = {
            2000,  // 10字
            1600,  // 8字
            1500,  // 7字
            1500,  // 7字 (APP算3字)
            1600,  // 8字
            1800,  // 9字
            1500,  // 7字 (去掉标点)
            1800,  // 9字
    };

    private static final long MEME_DUR = 1500;

    // 时间轴计算
    private long img1Start() { return 0; }
    private long img1Dur() { return SUB_DUR[0] + SUB_DUR[1]; }

    private long img2Start() { return img1Start() + img1Dur(); }
    private long img2Dur() { return SUB_DUR[2] + SUB_DUR[3]; }

    private long meme1Start() { return img2Start() + img2Dur(); }

    private long img3Start() { return meme1Start() + MEME_DUR; }
    private long img3Dur() { return SUB_DUR[4] + SUB_DUR[5]; }

    private long meme2Start() { return img3Start() + img3Dur(); }

    private long img4Start() { return meme2Start() + MEME_DUR; }
    private long img4Dur() { return SUB_DUR[6] + SUB_DUR[7]; }

    private long totalDur() { return img4Start() + img4Dur(); }

    private long subStart(int idx) {
        if (idx == 0) return img1Start();
        if (idx == 1) return img1Start() + SUB_DUR[0];
        if (idx == 2) return img2Start();
        if (idx == 3) return img2Start() + SUB_DUR[2];
        if (idx == 4) return img3Start();
        if (idx == 5) return img3Start() + SUB_DUR[4];
        if (idx == 6) return img4Start();
        if (idx == 7) return img4Start() + SUB_DUR[6];
        return 0;
    }

    @Test
    void testBuild() throws Exception {
        long total = totalDur();
        System.out.println("=== 千问奶茶事件视频 ===");
        System.out.println("总时长: " + total + "ms (" + (total / 1000.0) + "s)");

        // 1. 创建项目
        CreateProjectRequest createReq = new CreateProjectRequest();
        createReq.setProjectId(PROJECT_ID);
        createReq.setProjectName("千问奶茶事件_小红书营销_v2");
        createReq.setWidth(1080);
        createReq.setHeight(1920);
        callApi("/api/project", createReq, "1. 创建项目");

        // 2-7. 图片+表情包（严格按分镜时间顺序穿插）
        addImage(200501L, SALE_PATH + "1.png", img1Start(), img1Dur(), "2. 图1 (hook)");
        addImage(200502L, SALE_PATH + "2.png", img2Start(), img2Dur(), "3. 图2 (爆料)");
        addImage(200511L, MEME_SHOCKED, meme1Start(), MEME_DUR, "4. 表情包-震惊");
        addImage(200503L, SALE_PATH + "3.png", img3Start(), img3Dur(), "5. 图3 (共鸣)");
        addImage(200512L, MEME_FUNNY, meme2Start(), MEME_DUR, "6. 表情包-搞笑");
        addImage(200504L, SALE_PATH + "4.png", img4Start(), img4Dur(), "7. 图4 (引导)");

        // 8. BGM
        AddAudioRequest bgm = new AddAudioRequest();
        bgm.setProjectId(PROJECT_ID);
        bgm.setScriptIndex(0);
        bgm.setAudioId(200600L);
        bgm.setAudioUrl(BGM_PATH);
        bgm.setStartTime(0L);
        bgm.setDuration(total);
        bgm.setMaterialTimeStart(0L);
        bgm.setMaterialTimeEnd(179000L);
        bgm.setVolume(-30);
        bgm.setFadeInDuration(1000);
        bgm.setFadeOutDuration(1000);
        callApi("/api/project/audio", bgm, "8. BGM (Just Kidding)");

        // 9-16. 配音
        for (int i = 0; i < 8; i++) {
            AddAudioRequest vo = new AddAudioRequest();
            vo.setProjectId(PROJECT_ID);
            vo.setScriptIndex(0);
            vo.setAudioId(200601L + i);
            vo.setAudioUrl(SALE_PATH + "voiceover_" + (i + 1) + ".mp3");
            vo.setStartTime(subStart(i));
            vo.setDuration(SUB_DUR[i]);
            vo.setMaterialTimeStart(0L);
            vo.setMaterialTimeEnd(SUB_DUR[i]);
            vo.setVolume(0);
            callApi("/api/project/audio", vo, (9 + i) + ". 配音" + (i + 1));
        }

        // 17-24. 字幕
        for (int i = 0; i < 8; i++) {
            addSubtitle(SUBTITLES[i], subStart(i), SUB_DUR[i],
                    (17 + i) + ". 字幕: " + SUBTITLES[i]);
        }

        // 25. 水印
        AddTextRequest watermark = new AddTextRequest();
        watermark.setProjectId(PROJECT_ID);
        watermark.setScriptIndex(0);
        watermark.setText("AI热点速递");
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

        // 26. 构建
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
