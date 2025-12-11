namespace UVM_Assembler.Assembler;

public class Instruction
{
    public InstructionType Type { get; set; }
    public int? B { get; set; }
    
    public Instruction(InstructionType type, int? b = null)
    {
        Type = type;
        B = b;
    }
    
    public byte[] ToBytes()
    {
        byte[] result = new byte[4];
        
        // Байт 0: биты 0-6 = код операции
        byte opcode = (byte)((int)Type & 0x7F);
        
        if (B.HasValue)
        {
            int bValue = B.Value;
            
            // Проверяем, что B помещается в 10 бит (0-1023)
            if (bValue < 0 || bValue > 1023)
                throw new ArgumentException($"B value {bValue} must fit in 10 bits (0-1023)");
            
            // Байт 0: код операции + бит 0 из B в бит 7
            result[0] = (byte)(opcode | ((bValue & 0x0001) << 7));
            
            // Байт 1: биты 1-8 из B (сдвиг на 1)
            result[1] = (byte)((bValue & 0x01FE) >> 1);
            
            // Байт 2: бит 9 из B (сдвиг на 9)
            result[2] = (byte)((bValue & 0x0200) >> 9);
        }
        else
        {
            result[0] = opcode;
            result[1] = 0;
            result[2] = 0;
        }
        
        result[3] = 0; // Всегда 0
        
        return result;
    }
    
    public override string ToString()
    {
        return B.HasValue ? $"{Type} {B.Value}" : $"{Type}";
    }
}