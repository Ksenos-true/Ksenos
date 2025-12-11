namespace UVM_Assembler.Assembler;

public class Assembler
{
    public static Program AssembleFromJsonFile(string inputPath)
    {
        string json = File.ReadAllText(inputPath);
        return Program.FromJson(json);
    }
    
    public static void SaveToBinaryFile(Program program, string outputPath)
    {
        byte[] bytes = program.Assemble();
        File.WriteAllBytes(outputPath, bytes);
    }
    
    public static void DisplayTestMode(Program program)
    {
        Console.WriteLine("Internal representation:");
        Console.WriteLine("========================");
        
        int address = 0;
        foreach (var instruction in program.Instructions)
        {
            byte[] bytes = instruction.ToBytes();
            string hex = BitConverter.ToString(bytes).Replace("-", "");
            Console.WriteLine($"[0x{address:X4}] {instruction}");
            Console.WriteLine($"  Bytes: [{string.Join(", ", bytes.Select(b => $"0x{b:X2}"))}]");
            Console.WriteLine($"  Hex: 0x{hex}");
            address += 4;
        }
    }
    
    public static Program LoadProgramFromBinary(string path)
    {
        byte[] bytes = File.ReadAllBytes(path);
        var program = new Program();
        
        // Парсим 4 байта за раз
        for (int i = 0; i < bytes.Length; i += 4)
        {
            if (i + 3 >= bytes.Length) break;
            
            byte b0 = bytes[i];
            byte b1 = bytes[i + 1];
            byte b2 = bytes[i + 2];
            byte b3 = bytes[i + 3];
            
            // Извлекаем код операции (биты 0-6)
            int opcode = b0 & 0x7F;
            
            // Извлекаем параметр B
            int b = ((b0 >> 7) & 0x01) |        // bit 0 (бит 7 из b0)
                    ((b1 & 0xFF) << 1) |        // bits 1-8 (из b1)
                    ((b2 & 0x01) << 9);         // bit 9 (из b2)
            
            InstructionType type = opcode switch
            {
                43 => InstructionType.LOAD_CONST,
                120 => InstructionType.READ_MEM,
                72 => InstructionType.WRITE_MEM,
                121 => InstructionType.DIVIDE,
                _ => throw new InvalidOperationException($"Unknown opcode: {opcode} at offset {i}")
            };
            
            // Для WRITE_MEM параметр B не используется
            if (type == InstructionType.WRITE_MEM)
                program.Instructions.Add(new Instruction(type));
            else
                program.Instructions.Add(new Instruction(type, b));
        }
        
        return program;
    }
}