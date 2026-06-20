const { detectBlueberries } = require("../../utils/api");

Page({
  data: {
    imagePath: "",
    conf: 0.5,
    loading: false,
    choosingSource: "",
    result: null,
    emptyResult: false,
    errorMessage: ""
  },

  chooseFromCamera() {
    this.chooseImage(["camera"], "camera");
  },

  chooseFromAlbum() {
    this.chooseImage(["album"], "album");
  },

  chooseImage(sourceType, sourceName) {
    this.setData({
      choosingSource: sourceName,
      errorMessage: ""
    });

    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType,
      sizeType: ["compressed"],
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0];
        if (!file || !file.tempFilePath) {
          this.setData({ errorMessage: "没有获取到图片" });
          return;
        }
        this.setData({
          imagePath: file.tempFilePath,
          result: null,
          emptyResult: false,
          errorMessage: ""
        });
      },
      fail: () => {
        this.setData({ errorMessage: "已取消选择图片" });
      },
      complete: () => {
        this.setData({ choosingSource: "" });
      }
    });
  },

  onConfChange(event) {
    this.setData({
      conf: Number(event.detail.value).toFixed(2)
    });
  },

  startDetect() {
    if (!this.data.imagePath || this.data.loading) {
      return;
    }

    this.setData({
      loading: true,
      errorMessage: "",
      result: null,
      emptyResult: false
    });

    detectBlueberries(this.data.imagePath, this.data.conf)
      .then((result) => {
        const rows = (result.results || []).map((item) => ({
          ...item,
          confidencePercent: `${(Number(item.confidence || 0) * 100).toFixed(1)}%`
        }));
        this.setData({
          result: {
            ...result,
            results: rows
          },
          emptyResult: rows.length === 0
        });
      })
      .catch((error) => {
        this.setData({ errorMessage: error.message || "检测失败" });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  previewSelectedImage() {
    if (!this.data.imagePath) {
      return;
    }
    wx.previewImage({
      urls: [this.data.imagePath],
      current: this.data.imagePath
    });
  },

  previewResultImage() {
    if (!this.data.result || !this.data.result.result_image_url) {
      return;
    }
    wx.previewImage({
      urls: [this.data.result.result_image_url],
      current: this.data.result.result_image_url
    });
  },

  reset() {
    this.setData({
      imagePath: "",
      result: null,
      emptyResult: false,
      errorMessage: ""
    });
  }
});
