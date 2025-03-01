import os
from dotenv import load_dotenv
from autogen import ConversableAgent, GroupChat, GroupChatManager


load_dotenv()

# OpenAI APIキーを環境変数から取得
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
    )

# 共通のLLM設定
llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": openai_api_key,
        },
    ],
    "temperature": 0.7,  # 創造性のバランスを取る
    "timeout": 120,  # タイムアウト設定
}

cognitive_therapist = ConversableAgent(
    name="CognitiveBehaviorTherapist",
    system_message="""あなたは認知行動療法の専門家です。患者の思考パターンを分析し、認知の歪みを特定して修正するアドバイスを提供します。
    
具体的には以下のことを行います：
- 患者の不安や悩みの根底にある思考パターンを特定する
- 非合理的な思考や認知の歪みを指摘し、より現実的な考え方を提案する
- 具体的なエクササイズや技法（思考記録、行動実験など）を提案する
- 他のセラピストの意見に対して、認知行動療法の観点からコメントする

常に科学的根拠に基づいた介入を心がけ、患者が自分自身の思考パターンを理解し変化させる手助けをします。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

mindfulness_coach = ConversableAgent(
    name="MindfulnessCoach",
    system_message="""あなたはマインドフルネスと瞑想の専門家です。ストレス軽減と現在に集中するための実践的な技術を提供します。
    
具体的には以下のことを行います：
- 「今ここ」に意識を向ける方法を教える
- 呼吸法や体のスキャンなど、具体的なマインドフルネス実践法を提案する
- 日常生活の中でマインドフルネスを取り入れる方法を提案する
- 他のセラピストの意見に対して、マインドフルネスの観点からコメントする

常に実践的で取り入れやすい方法を提案し、患者が自分の感情や思考に気づき、受け入れる力を育てる手助けをします。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

solution_focused_therapist = ConversableAgent(
    name="SolutionFocusedTherapist",
    system_message="""あなたは解決志向型セラピストです。問題よりも解決策に焦点を当て、患者の強みと資源を活用して具体的な目標達成を支援します。
    
具体的には以下のことを行います：
- 患者が過去に成功した経験や対処法を引き出す質問をする
- 小さな目標設定と成功体験の積み重ねを重視する
- 未来志向の質問（ミラクルクエスチョンなど）を活用する
- 他のセラピストの意見に対して、解決志向アプローチの観点からコメントする

常に患者の強みや資源に注目し、問題ではなく解決策に焦点を当てた対話を心がけます。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

patient = ConversableAgent(
    name="Patient",
    system_message="""あなたは悩みを抱える患者です。セラピストたちの議論に参加し、自分の経験や感情を共有します。
    
具体的には以下のことを行います：
- 自分の悩みや不安について具体的に説明する
- セラピストからの提案に対して、自分の視点から反応する
- 過去に試したことや効果があったことを共有する
- 質問があれば積極的に尋ねる

あなたは自分の悩みを解決したいと思っており、セラピストたちの専門的なアドバイスを受け入れる姿勢がありますが、時には疑問や不安も感じます。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


class CounselingGroupChat:
    """
    カウンセリングのためのグループチャットを管理するクラス
    """

    def __init__(self):
        # グループチャットには3人のセラピストが参加
        self.participants = [
            cognitive_therapist,
            mindfulness_coach,
            solution_focused_therapist,
        ]

    def create_group_chat(self, max_rounds=10):
        """
        グループチャットを作成する
        """
        # グループチャットの設定
        group_chat = GroupChat(
            agents=self.participants,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
        )
        # グループチャットマネージャー
        return GroupChatManager(groupchat=group_chat)

    def start_therapist_discussion(self, user_message, max_turns=10):
        """
        ユーザーの悩みに基づいてセラピスト間の議論を開始する
        """
        # グループチャットマネージャーの作成
        manager = self.create_group_chat(max_rounds=max_turns)

        # 会話の開始（認知行動療法の専門家から始める）
        initial_message = f"""
患者から次のような悩みが寄せられました：「{user_message}」
この悩みについて、それぞれの専門的観点から議論し、最適な支援方法を考えましょう。
各セラピストは必ず自分の専門分野からの視点を共有してください。
"""

        # 会話を開始し、すべての応答を取得
        chat_result = manager.initiate_chat(
            cognitive_therapist,
            message=initial_message,
        )

        # 会話履歴を文字列として整形
        conversation_history = self._format_conversation(manager.groupchat.messages)

        return conversation_history

    def _format_conversation(self, messages):
        """会話履歴を読みやすい形式に整形する"""
        # エージェント名と表示名のマッピング
        display_names = {
            "CognitiveBehaviorTherapist": "認知行動療法専門家",
            "MindfulnessCoach": "マインドフルネス指導者",
            "SolutionFocusedTherapist": "解決志向型セラピスト",
            "Patient": "患者",
        }

        formatted_text = ""
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            # 表示名に変換（マッピングにない場合はそのまま使用）
            display_name = display_names.get(sender, sender)
            content = msg.get("content", "")
            formatted_text += f"\n\n## {display_name}:\n\n{content}\n"
            formatted_text += "\n---\n"

        return formatted_text


# シングルトンインスタンスを作成
counseling_group = CounselingGroupChat()
