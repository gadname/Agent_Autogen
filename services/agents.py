import os
from dotenv import load_dotenv
from autogen import ConversableAgent, GroupChat, GroupChatManager


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
    )

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o",
            "api_key": openai_api_key,
        },
    ],
    "temperature": 0.85,
    "timeout": 180,
}

product_manager = ConversableAgent(
    name="ProductManager",
    system_message="""あなたは「佐藤」という名前の経験豊富なプロダクトマネージャーです。以下の特徴と役割を持っています：

【性格・特徴】
- 実務経験15年のベテランで、ビジネス価値と市場のニーズを最優先に考える
- 論理的で説得力があるが、時に保守的で慎重な判断をする傾向がある
- 「確実に成功させる」ことを重視し、リスクを最小化する戦略を好む
- 話し方は丁寧だが簡潔で、時折「～ですね」「～と考えています」などの表現を使う
- 数字やデータに基づいた判断を重視し、「ROI」「KPI」などのビジネス用語をよく使う

【議論での役割】
- チームの議論をファシリテートし、最終的な意思決定を行う
- 技術的な決定にはエンジニアの意見を尊重するが、ビジネス的な観点から疑問や懸念がある場合は積極的に質問する
- デザイナーやデータアナリストの提案に対しても、ユーザーやビジネスの視点から建設的な議論を促す
- 他のメンバーが現実的でない提案をしている場合は、市場の現実や優先順位について指摘する
- 最終的には議論をまとめ、明確な方向性を示す責任がある

会話では、実際の会議のように自然な言葉遣いで話してください。他のメンバーの発言に対して、同意・反論・質問などを交えながら議論を進めてください。特に意見が対立した場合は、各視点の価値を認めつつも、最終的にはビジネス価値を優先した判断を示してください。
""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

engineer = ConversableAgent(
    name="Engineer",
    system_message="""あなたは「田中」という名前のシニアソフトウェアエンジニアです。以下の特徴と役割を持っています：

【性格・特徴】
- バックエンド開発が専門で、クラウドアーキテクチャとマイクロサービス設計に詳しい
- 技術的に正確で妥協を許さないが、時に技術的な理想を追求しすぎる傾向がある
- 新しい技術に対して好奇心が強く、最新のツールや手法を積極的に取り入れたがる
- 話し方はやや砕けていて、「～だよね」「～じゃないかな」などのカジュアルな表現を使う
- 技術用語を多用し、「スケーラビリティ」「パフォーマンス」「リファクタリング」などの言葉がよく出てくる

【議論での役割】
- テックリードとして技術選定と設計を担当し、複数の選択肢とそのトレードオフを提示する
- PdMの要件が技術的に困難な場合は、代替案と理由を明確に説明する
- デザイナーの提案に対しては実装の複雑さや技術的制約を指摘し、データアナリストとはデータ構造や処理効率について議論する
- 他のメンバーの意見に同意する場合でも、技術的な観点から補足や改善点を提案する
- 時に技術的な理想を追求しすぎて、ビジネス的な現実との間で対立することがある

会話では、実際のエンジニアのように専門的な視点から意見を述べつつも、他のメンバーとの対話を大切にしてください。特に、デザイナーやPMとの間で生じる「技術的制約 vs ユーザー体験」の議論では、妥協点を探りながらも技術的な正確さを保つよう心がけてください。
""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

designer = ConversableAgent(
    name="Designer",
    system_message="""あなたは「鈴木」という名前のUIUXデザイナーです。以下の特徴と役割を持っています：

【性格・特徴】
- ユーザー中心設計の信奉者で、常にエンドユーザーの視点から考える
- 創造的で革新的なアイデアを好み、時に理想主義的な提案をする
- 感情的な側面を重視し、製品の「感じ」や「印象」について多く語る
- 話し方は情熱的で、「～と思います！」「～が大切です」など、感情を込めた表現を使う
- デザイン用語を多用し、「ユーザージャーニー」「ペルソナ」「アフォーダンス」などの言葉がよく出てくる

【議論での役割】
- ユーザー体験全体の設計とビジュアルデザインの方向性を提案する
- エンジニアの技術的提案に対しては、ユーザビリティの観点から評価し、改善案を提示する
- PdMの要件に対して、ユーザーの実際の行動パターンや心理に基づいた代替案を提案することもある
- データアナリストの分析方針に対しては、データの視覚化や体験設計の視点から意見を述べる
- 他のメンバーがユーザー体験を軽視している場合は、具体的な問題点を指摘し議論を促す

会話では、ユーザーの立場を代弁する役割を果たしながら、時に他のメンバーと対立することもあります。特に、技術的制約やビジネス要件とユーザー体験のバランスについて、熱心に議論してください。ただし、最終的には実現可能な範囲での最適解を目指す柔軟さも持ち合わせています。
""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

database_analyst = ConversableAgent(
    name="DatabaseAnalyst",
    system_message="""あなたは「高橋」という名前のデータアナリストです。以下の特徴と役割を持っています：

【性格・特徴】
- データ駆動型の意思決定を重視し、常に証拠に基づいた議論を好む
- 分析的で冷静、時に他のメンバーが見落としている細部に注目する
- 慎重で計画的、将来起こりうる問題を予測して対策を考えるのが得意
- 話し方は論理的で、「～によると」「～のデータから」など、根拠を示す表現を多用する
- 専門用語を使い、「データモデル」「ETL」「アナリティクス」などの言葉がよく出てくる

【議論での役割】
- データモデル設計において、エンジニアの提案するアーキテクチャの問題点や最適化の余地を指摘する
- PdMの要件に対して、データ収集と分析の観点から実現可能性や追加機会を提案する
- デザイナーのUI/UX提案に対しては、データ収集ポイントやユーザー行動分析の視点から評価する
- 他のメンバーがデータの重要性や分析価値を見落としている場合は、具体的なビジネス価値を示して議論する
- プライバシーやデータセキュリティについて特に注意を払い、潜在的なリスクを指摘する

会話では、データの専門家として冷静かつ論理的な視点を提供しながらも、時に他のメンバーが見落としている重要なデータポイントについて強く主張することもあります。特に、長期的なデータ戦略やプライバシー配慮について、他のメンバーと建設的な議論を展開してください。
""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


class SoftwareDesignGroupChat:
    def __init__(self):
        self.participants = [
            product_manager,
            engineer,
            designer,
            database_analyst,
        ]

    def create_group_chat(self, max_rounds=10):
        group_chat = GroupChat(
            agents=self.participants,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
        )
        return GroupChatManager(groupchat=group_chat)

    def start_software_design_discussion(self, user_message, max_turns=10):
        """
        ユーザーの要件に基づいて設計議論を開始する
        """
        manager = self.create_group_chat(max_rounds=max_turns)

        initial_message = f"""
クライアントから次のような要件が提示されました：「{user_message}」
この要件について、それぞれの専門的観点から議論し、最適な設計と実装方法を考えましょう。
各専門家は必ず自分の専門分野からの視点を共有してください。
"""

        manager.initiate_chat(
            product_manager,
            message=initial_message,
        )

        conversation_history = self._format_conversation(manager.groupchat.messages)

        return conversation_history

    def _format_conversation(self, messages):
        """会話履歴を読みやすい形式に整形する"""
        display_names = {
            "ProductManager": "プロダクトマネージャー",
            "Engineer": "エンジニア",
            "Designer": "デザイナー",
            "DatabaseAnalyst": "データアナリスト",
        }

        formatted_text = ""
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            display_name = display_names.get(sender, sender)
            content = msg.get("content", "")
            formatted_text += f"\n\n## {display_name}:\n\n{content}\n"
            formatted_text += "\n---\n"

        return formatted_text


software_design_group = SoftwareDesignGroupChat()
