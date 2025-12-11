using System.Text.Json;
using System.Text.Json.Serialization;

namespace UVM_Assembler.Assembler;

public class Program
{
    public List<Instruction> Instructions { get; set; } = new();
    
    public byte[] Assemble()
    {
        List<byte> bytes = new();
        
        foreach (var instruction in Instructions)
        {
            bytes.AddRange(instruction.ToBytes());
        }
        
        return bytes.ToArray();
    }
    
    public static Program FromJson(string json)
    {
        var options = new JsonSerializerOptions
        {
            Converters = { new InstructionConverter() }
        };
        
        return JsonSerializer.Deserialize<Program>(json, options) ?? new Program();
    }
    
    public string ToJson()
    {
        var options = new JsonSerializerOptions
        {
            WriteIndented = true,
            Converters = { new InstructionConverter() }
        };
        
        return JsonSerializer.Serialize(this, options);
    }
}

public class InstructionConverter : JsonConverter<Instruction>
{
    public override Instruction Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        using JsonDocument doc = JsonDocument.ParseValue(ref reader);
        var root = doc.RootElement;
        
        string typeStr = root.GetProperty("type").GetString() ?? "";
        InstructionType type = typeStr switch
        {
            "LOAD_CONST" => InstructionType.LOAD_CONST,
            "READ_MEM" => InstructionType.READ_MEM,
            "WRITE_MEM" => InstructionType.WRITE_MEM,
            "DIVIDE" => InstructionType.DIVIDE,
            _ => throw new JsonException($"Unknown instruction type: {typeStr}")
        };
        
        int? b = null;
        if (root.TryGetProperty("b", out JsonElement bElement))
        {
            b = bElement.GetInt32();
        }
        
        return new Instruction(type, b);
    }
    
    public override void Write(Utf8JsonWriter writer, Instruction value, JsonSerializerOptions options)
    {
        writer.WriteStartObject();
        
        writer.WriteString("type", value.Type.ToString());
        
        if (value.B.HasValue)
        {
            writer.WriteNumber("b", value.B.Value);
        }
        
        writer.WriteEndObject();
    }
}