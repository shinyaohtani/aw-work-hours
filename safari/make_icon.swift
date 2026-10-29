// 同期マークのアイコン PNG を作る（拡張機能の extension/images/icon-*.png 用）: swift safari/make_icon.swift <出力先.png> <ピクセル数>
import AppKit

let args = CommandLine.arguments
let outPath = args[1]
let px = CGFloat(Double(args[2])!)

let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil, pixelsWide: Int(px), pixelsHigh: Int(px), bitsPerSample: 8,
    samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
    bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)

// macOS アイコンの余白（約10%）と角丸を付けた epoch の青の地
let inset = px * 0.1
let body = NSRect(x: inset, y: inset, width: px - inset * 2, height: px - inset * 2)
NSColor(srgbRed: 0x00 / 255, green: 0x41 / 255, blue: 0xC0 / 255, alpha: 1).setFill()
NSBezierPath(roundedRect: body, xRadius: body.width * 0.225, yRadius: body.width * 0.225).fill()

// 白の同期マーク
let config = NSImage.SymbolConfiguration(pointSize: body.width * 0.5, weight: .semibold)
    .applying(.init(paletteColors: [.white]))
let symbol = NSImage(systemSymbolName: "arrow.triangle.2.circlepath", accessibilityDescription: nil)!
    .withSymbolConfiguration(config)!
let size = symbol.size
symbol.draw(in: NSRect(x: (px - size.width) / 2, y: (px - size.height) / 2, width: size.width, height: size.height))

NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: outPath))
