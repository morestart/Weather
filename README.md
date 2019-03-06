# HomeAssistant 天气卡

## 效果图

![图](https://github.com/morestart/weather/blob/master/view.png)


## 使用方法：

- 在HA中建立以下路径`home assistant\custom_components\he_weather\weather.py`
- 或者使用此命令下载 `curl -O https://raw.githubusercontent.com/morestart/weather/master/weather.py`

如果HA中不存在以上路径，请参照图示自行建立即可。

## 配置内容如下

```yaml
weather:
  - platform: he_weather
    api_key: key
    id: auto_ip 或者 填写城市名称 eg（北京，beijing）
```

