/**
 * 设备指纹工具
 * 用于账号共享检测
 */

/**
 * 生成 Canvas 指纹
 */
function getCanvasFingerprint() {
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    canvas.width = 200
    canvas.height = 50

    ctx.textBaseline = 'top'
    ctx.font = '14px Arial'
    ctx.fillStyle = '#f60'
    ctx.fillRect(125, 1, 62, 20)
    ctx.fillStyle = '#069'
    ctx.fillText('Hello, World!', 2, 15)
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)'
    ctx.fillText('Hello, World!', 4, 17)

    return canvas.toDataURL().slice(-50)
  } catch (e) {
    return 'unsupported'
  }
}

/**
 * 生成 Audio 指纹
 */
function getAudioFingerprint() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext
    if (!AudioContext) return 'unsupported'

    const context = new AudioContext()
    const oscillator = context.createOscillator()
    const analyser = context.createAnalyser()
    const gainNode = context.createGain()
    const scriptProcessor = context.createScriptProcessor(4096, 1, 1)

    gainNode.gain.value = 0
    oscillator.connect(analyser)
    analyser.connect(scriptProcessor)
    scriptProcessor.connect(gainNode)
    gainNode.connect(context.destination)

    oscillator.start(0)
    const fingerprint = analyser.frequencyBinCount.toString()

    oscillator.stop()
    context.close()

    return fingerprint
  } catch (e) {
    return 'unsupported'
  }
}

/**
 * 获取浏览器信息
 */
function getBrowserInfo() {
  const ua = navigator.userAgent
  let browserFamily = 'Unknown'
  let browserMajor = '0'

  if (ua.indexOf('Chrome') > -1 && ua.indexOf('Edg') === -1) {
    browserFamily = 'Chrome'
    const match = ua.match(/Chrome\/(\d+)/)
    if (match) browserMajor = match[1]
  } else if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) {
    browserFamily = 'Safari'
    const match = ua.match(/Version\/(\d+)/)
    if (match) browserMajor = match[1]
  } else if (ua.indexOf('Firefox') > -1) {
    browserFamily = 'Firefox'
    const match = ua.match(/Firefox\/(\d+)/)
    if (match) browserMajor = match[1]
  } else if (ua.indexOf('Edg') > -1) {
    browserFamily = 'Edge'
    const match = ua.match(/Edg\/(\d+)/)
    if (match) browserMajor = match[1]
  }

  return { browserFamily, browserMajor }
}

/**
 * 收集设备指纹
 * @returns {Object} 设备指纹数据
 */
export function collectFingerprint() {
  const { browserFamily, browserMajor } = getBrowserInfo()

  const fingerprint = {
    screen_width: screen.width,
    screen_height: screen.height,
    device_pixel_ratio: window.devicePixelRatio || 1,
    color_depth: screen.colorDepth || 24,
    timezone_offset: new Date().getTimezoneOffset(),
    locale: navigator.language || 'en-US',
    platform: navigator.platform || 'Unknown',
    browser_family: browserFamily,
    browser_major: browserMajor,
    hardware_concurrency: navigator.hardwareConcurrency || 0,
    touch_support: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
    canvas_hash: getCanvasFingerprint(),
    audio_hash: getAudioFingerprint()
  }

  return fingerprint
}

/**
 * 生成指纹哈希
 * @param {Object} fingerprint 指纹数据
 * @returns {Promise<string>} SHA-256 哈希值
 */
export async function generateFingerprintHash(fingerprint) {
  const str = JSON.stringify(fingerprint)
  const encoder = new TextEncoder()
  const data = encoder.encode(str)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  return hashHex
}
