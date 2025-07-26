declare module 'lamejs-fixed' {
  export class Mp3Encoder {
    constructor(channels: number, sampleRate: number, bitRate: number);
    encodeBuffer(left: Int16Array, right: Int16Array): Int8Array;
    flush(): Int8Array;
  }
  
  export class WavHeader {
    static RIFF: number;
    static WAVE: number;
    static fmt_: number;
    static data: number;
    static readHeader(dataView: DataView): unknown;
  }
}